import requests
from bs4 import BeautifulSoup
import re
import time
from dotenv import load_dotenv
import os
# 导入 dotenv
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()

# 使用环境变量
NCBI_EMAIL = os.getenv('NCBI_EMAIL')
NCBI_TOOL = os.getenv('NCBI_TOOL')
NCBI_KEY = os.getenv('NCBI_KEY')

def clean_text(text: str) -> str:
    """清理文本，移除 XML/HTML 标签和多余的空白字符"""
    try:
        # 使用 lxml 解析器处理 XML
        soup = BeautifulSoup(text, 'lxml-xml')
    except:
        # 如果 lxml-xml 解析失败，回退到 lxml HTML 解析器
        soup = BeautifulSoup(text, 'lxml')
    
    clean = soup.get_text()
    
    # 清理空白行和多余的空格
    lines = [line.strip() for line in clean.split('\n')]
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)

def get_gene_info(query: str) -> str:
    """获取基因信息并返回清理后的文本"""
    url = "https://ncbi.nlm.nih.gov/gene/"
    params = {
        "db": "gene",
        "term": query,
        "report": "docsum",
        "format": "text"
    }
    response = requests.get(url, params=params)
    # return clean_text(response.text)
    return BeautifulSoup(response.text, 'lxml-xml').get_text()

def get_snp_info(query: str) -> str:
    """获取 SNP 信息并返回清理后的文本"""
    url = "https://www.ncbi.nlm.nih.gov/snp/"
    params = {
        "db": "snp",
        "term": query,
        "report": "docsum",
        "format": "text"
    }
    response = requests.get(url, params=params)
    # return clean_text(response.text)
    return BeautifulSoup(response.text, 'lxml-xml').get_text()

def blast_sequence(sequence: str) -> str:
    """对DNA序列进行BLAST比对"""
    try:
        # 提交BLAST请求
        params = {
            "CMD": "Put",
            "PROGRAM": "blastn",
            "MEGABLAST": "on",
            "QUERY": sequence,
            "DATABASE": "core_nt",
        }
        response = requests.get(
            "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi",
            params=params
        )
        
        # 从响应中提取RID
        rid = None
        for line in response.text.split("\n"):
            if line.startswith("    RID = "):
                rid = line.split(" = ")[1].strip()
                break

        if not rid:
            return "Failed to get BLAST RID"

        # 等待结果
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(10)
            params = {
                "CMD": "Get",
                "FORMAT_TYPE": "Text",
                "RID": rid,
                "ALIGNMENTS": "5",
                "DESCRIPTIONS": "5"
            }
            response = requests.get(
                "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi",
                params=params
            )
            
            if "Status=WAITING" not in response.text:
                break
                
            if attempt == max_attempts - 1:
                return "Timeout waiting for BLAST results"

        # 解析并返回完整的BLAST结果
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def _submit_blast_request(params: dict) -> str:
    """
    Generic function to submit BLAST request and get results
    
    Args:
        params: Dictionary containing essential BLAST parameters
    Returns:
        str: BLAST results text
    """
    try:
        # 1. 初始化请求
        submit_url = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
        submit_params = {**params, "CMD": "Put"}
        
        # 2. 发送初始请求并检查状态
        response = requests.get(submit_url, params=submit_params)
        response.raise_for_status()  # 立即检查HTTP错误
        
        # 3. 提取RID - 使用更简单的字符串操作
        rid = None
        response_lines = response.text.split("\n")  # 只分割一次文本
        for line in response_lines:
            if "RID =" in line:  # 使用简单的字符串包含检查
                rid = line.split("=")[1].strip()  # 简化分割操作
                break

        if not rid:
            return "Failed to get BLAST RID"

        # 4. 设置结果获取参数
        result_params = {
            "CMD": "Get",
            "RID": rid,
            "ALIGNMENTS": "1",
            "DESCRIPTIONS": "5",
            "FORMAT_TYPE": "Text",
            # "ALIGNMENT_VIEW": "Tabular"
        }

        # 5. 使用简单轮询替代递归
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(3)  # 固定等待时间
            
            # 6. 获取结果
            result_response = requests.get(submit_url, params=result_params)
            result_response.raise_for_status()
            
            # 7. 检查结果状态
            if "Status=WAITING" not in result_response.text:
                return BeautifulSoup(result_response.text, 'lxml-xml').get_text()
                
        return "Timeout waiting for BLAST results"
        
    # 8. 错误处理分离
    except requests.RequestException as e:
        return f"Request Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def blastn(sequence: str) -> str:
    """
    Perform BLASTN search (nucleotide vs nucleotide)
    
    Use case:
    - Find similar DNA sequences
    - Genome sequence alignment
    - Primer design and validation
    - Species identification
    
    Args:
        sequence: Input DNA sequence
    """
    params = {
        "PROGRAM": "blastn",
        "QUERY": sequence,
        "MEGABLAST": "on",
        "DATABASE": "core_nt"
    }
    return _submit_blast_request(params)

def blastp(sequence: str) -> str:
    """
    Perform BLASTP search (protein vs protein)
    
    Use case:
    - Protein homology analysis
    - Domain prediction
    - Evolutionary relationship study
    - Protein family analysis
    
    Args:
        sequence: Input protein sequence
    """
    params = {
        "PROGRAM": "blastp",
        "QUERY": sequence,
        "DATABASE": "nr"
    }
    return _submit_blast_request(params)

def blastx(sequence: str) -> str:
    """
    Perform BLASTX search (translated nucleotide vs protein)
    
    Use case:
    - Predict coding regions
    - EST sequence annotation
    - Novel gene function prediction
    - Cross-species gene homology analysis
    
    Args:
        sequence: Input DNA sequence
    """
    params = {
        "PROGRAM": "blastx",
        "QUERY": sequence,
        "DATABASE": "nr"
    }
    return _submit_blast_request(params)

def tblastn(sequence: str) -> str:
    """
    Perform TBLASTN search (protein vs translated nucleotide)
    
    Use case:
    - Find genes encoding specific proteins
    - Discover new homologous genes
    - Cross-species gene prediction
    - Genome annotation
    
    Args:
        sequence: Input protein sequence
    """
    params = {
        "PROGRAM": "tblastn",
        "QUERY": sequence,
        "DATABASE": "core_nt"
    }
    return _submit_blast_request(params)

def tblastx(sequence: str) -> str:
    """
    Perform TBLASTX search (translated nucleotide vs translated nucleotide)
    
    Use case:
    - Find evolutionarily distant homologous genes
    - Analyze unknown DNA sequences
    - Cross-species gene structure analysis
    - Novel gene prediction and annotation
    
    Args:
        sequence: Input DNA sequence
    """
    params = {
        "PROGRAM": "tblastx",
        "QUERY": sequence,
        "DATABASE": "core_nt"
    }
    return _submit_blast_request(params)

def get_gene_summary(gene_id: str) -> str:
    """
    使用 Biopython 从 NCBI Entrez 获取基因摘要信息
    
    Args:
        gene_id: 基因ID (例如: 'BRCA1', 'ENSG00000012048')
        
    Returns:
        str: 基因的名称和功能描述摘要信息
    """
    from Bio import Entrez
    
    # 设置 Entrez email
    Entrez.email = NCBI_EMAIL
    Entrez.tool = NCBI_TOOL
    Entrez.api_key = NCBI_KEY
    
    try:
        # 搜索基因
        with Entrez.esearch(db="gene", term=gene_id, sort="relevance") as handle:
            record = Entrez.read(handle)

        # 获取基因摘要信息
        with Entrez.esummary(db="gene", id=record['IdList'][0]) as handle:
            summary = Entrez.read(handle)
        
        gene_summary = summary["DocumentSummarySet"]['DocumentSummary'][0]['Name']+":"+summary["DocumentSummarySet"]['DocumentSummary'][0]['Summary']
        return gene_summary.strip()
    except Exception as e:
        return f"获取基因 {gene_id} 的摘要信息时发生错误: {str(e)}"
        


if __name__ == "__main__":
    # print(get_gene_info("BRCA1")) # symbol name 
    # print("="*50) 
    # print(get_gene_info("ENSG10010137169.1")) # ensembl id
    # print("="*50) 
    # print(get_gene_info("ELiver failure")) # disease name
    # print("="*50) 
    # print(get_snp_info("1217074595")) # rs id
    # print("="*50) 
    # print(get_snp_info("rs1217074595")) # rs id with rs prefix 

    # DNA sequence example
    dna_seq = "CGTACACCATTGGTGCCAGTGACTGTGGTCAATTCGGTAGAAGTAGAGGTAAAAGTGCTGTTCCATGGCTCAGTTGTAGTTATGATGGTGCTAGCAGTTGTTGGAGTTCTGATGACAATGACGGTTTCGTCAGTTG"
    print("BLASTN results:")
    print(blastn(dna_seq))
    
    # print("="*50)
    # # Protein sequence example
    # protein_seq = "mvlspadktnvkaawgkvgahageygaealermflsfpttktyfphfdlshgsaqvkghgkkvadaltnavahvddmpkalsalsdlhahklrvdpvnfk"
    # print("\nBLASTP results:")
    # print(blastp(protein_seq))

    print("="*50)
    print(get_gene_summary("BRCA1"))


