from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from bridge_llm.llm_openai import chat_openai
from bridge_llm.llm_ollama import chat_ollama_llama31, chat_ollama_llama31_fp16, chat_ollama_llama32_3b_fp16, chat_ollama_llama31_70b
from bridge_llm.llm_openrouter import chat_openrouter
from bridge_llm.llm_doubao import chat_doubao
from bridge_llm.llm_deepseek import chat_deepseek
from langchain_core.prompts import ChatPromptTemplate
import time
from tools.ncbitools import get_gene_info, get_snp_info, blastn, blastp, blastx, tblastx, tblastn , _submit_blast_request

# langsmith tracing
# load env
from dotenv import load_dotenv
load_dotenv('/home/awgao/BioinfoGPT/.env',verbose=True)

# select llm
# current_llm = chat_ollama_llama31_fp16
# current_llm = chat_doubao
# current_llm = chat_ollama_llama31 
current_llm = chat_openai

def trim_text(text: str) -> str:
    """修剪搜索结果，只要前5个结果"""
    try:
        return text.split('\n\n10.')[0]
    except:
        return text

@tool
def get_gene_info(query: str) -> str:
    """获取基因信息，输入可以是基因符号名称、ensembl ID或疾病名称"""
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

@tool
def get_snp_info(query: str) -> str:
    """获取SNP信息，输入可以是rs ID（带或不带rs前缀）"""
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

# 使用import 导入的函数，构建tools
@tool
def search_gene_info(query: str) -> str:
    """Get gene information from NCBI database.
    
    Args:
        query (str): Query string, can be one of:
            - Gene symbol (e.g., 'BRCA1')
            - Ensembl ID (e.g., 'ENSG00000012048')
            - Disease name (e.g., 'Breast cancer')
    
    Returns:
        str: their official symbols, names, aliases, designations, chromosomes, locations, annotations, MIM numbers, and IDs. 
    """
    print(query)
    result = get_gene_info(query)
    trimmed_result = trim_text(result)
    return trimmed_result

@tool
def search_snp_info(query: str) -> str:
    """Get detailed SNP information from NCBI database.
    
    This function queries the NCBI SNP database and returns comprehensive SNP variant information including:
    - SNP ID and species information
    - Variant type and specific changes
    - Chromosomal positions (both GRCh37 and GRCh38)
    - Associated genes
    - Functional consequences
    - Validation status
    - Global Minor Allele Frequency (MAF)
    - HGVS notation
    
    Args:
        query (str): SNP identifier, can be either:
            - Complete rs ID (e.g., 'rs983419152')
            - Numeric ID without 'rs' prefix (e.g., '983419152')
    
    Returns:
        str: Formatted text containing detailed SNP information as listed above
        
    """
    print(query)
    result = get_snp_info(query)    
    trimmed_result = trim_text(result)
    return trimmed_result

@tool
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
    print(params)
    report = _submit_blast_request(params)
    trimmed_report = ''.join(report.split('>')[0])
    return trimmed_report


@tool
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
    report = _submit_blast_request(params)
    trimmed_report = ''.join(report.split('>')[0:1])
    return trimmed_report


@tool
def blastx(sequence: str) -> str:
    """
    Perform BLASTX search (nucleotide vs protein)
    
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
    report = _submit_blast_request(params)
    trimmed_report = ''.join(report.split('>')[0:1])
    return trimmed_report


@tool
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
        "PROGRAM": "tblastn",
        "QUERY": sequence,
        "DATABASE": "core_nt"
    }
    report = _submit_blast_request(params)
    trimmed_report = ''.join(report.split('>')[0:1])
    return trimmed_report



@tool
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
        "PROGRAM": "tblastx",
        "QUERY": sequence,
        "DATABASE": "core_nt"
    }
    report = _submit_blast_request(params)
    trimmed_report = ''.join(report.split('>')[0:1])
    return trimmed_report

@tool
def blastn_untrimmed(sequence: str) -> str:
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
    report = _submit_blast_request(params)
    return report

    
# tools = [get_gene_info, get_snp_info, blastn, blastp, blastx, tblastx, tblastn]
# tools_from_import = [search_gene_info, search_snp_info, blastn, blastp, blastx, tblastx, tblastn]

# tools_from_import_untrimmed = [search_gene_info, search_snp_info, blastn_untrimmed]

tools = [search_gene_info, search_snp_info, blastn]


# 创建一个agent with tools
agent = create_react_agent(model=current_llm, tools=tools)

# agent_use_import_tools = create_react_agent(model=current_llm, tools=tools_from_import)
# agent_use_import_tools_untrimmed = create_react_agent(model=current_llm, tools=tools_from_import_untrimmed)
# 运行agent

# response = agent.invoke({"messages": [HumanMessage(content="Which chromosome is TTTY7 gene located on human genome?")]})
# print(response["messages"][-1].content)


# model bind tools

# genemodel = chat_openai.bind_tools(tools)
# response = genemodel.invoke([HumanMessage(content="Which gene is SNP rs1217074595 associated with")])

# main 测试

if __name__ == "__main__":
    test_questions = [
        "Is ATP5F1EP2 a protein-coding gene?",
        "Is LOC124907753 a protein-coding gene?",
        "Is AMD1P4 a protein-coding gene?",
        "Is NODAL a protein-coding gene?",
        "Is MIR4436B2 a protein-coding gene?",
        "Is NAXE a protein-coding gene?",
        "Is LOC124909477 a protein-coding gene?",
        "Is LINC01560 a protein-coding gene?",
        "Is UCKL1-AS1 a protein-coding gene?",
        "Is MIR6843 a protein-coding gene?",
        "Is RPL7AP58 a protein-coding gene?",
        "Is SERF2 a protein-coding gene?",
        "Is LOC124907937 a protein-coding gene?",
        "Is RNU6-1193P a protein-coding gene?",
        "Is LOC124903168 a protein-coding gene?",
        "Is HMGB1P9 a protein-coding gene?",
        "Is LOC100420990 a protein-coding gene?",
        "Is RNU6-1212P a protein-coding gene?",
        "Is CPVL-AS2 a protein-coding gene?",
        "Is NPFFR1 a protein-coding gene?",
        "Is CYP4F10P a protein-coding gene?",
        "Is FANCG a protein-coding gene?",
        "Is CMKLR2 a protein-coding gene?",
        "Is SSBP3-AS1 a protein-coding gene?",
        "Is LOC100419835 a protein-coding gene?",
        "Is RNU7-171P a protein-coding gene?",
        "Is RPL34P34 a protein-coding gene?",
        "Is LOC100526841 a protein-coding gene?",
        "Is TTLL1 a protein-coding gene?",
        "Is CORO1A-AS1 a protein-coding gene?",
        "Is SPARC a protein-coding gene?",
        "Is LOC100129457 a protein-coding gene?",
        "Is HOTAIR a protein-coding gene?",
        "Is CAAP1 a protein-coding gene?",
        "Is PIGCP1 a protein-coding gene?",
        "Is LINC01054 a protein-coding gene?",
        "Is SPOP a protein-coding gene?",
        "Is RNU6-746P a protein-coding gene?",
        "Is POLE4P1 a protein-coding gene?",
        "Is RASSF3-DT a protein-coding gene?",
        "Is RPL31P19 a protein-coding gene?",
        "Is FBXO3-DT a protein-coding gene?",
        "Is DNAJB6P2 a protein-coding gene?",
        "Is LINC02865 a protein-coding gene?",
        "Is AFF1 a protein-coding gene?",
        "Is PWWP2A a protein-coding gene?",
        "Is LOC105369759 a protein-coding gene?",
        "Is B3GAT1 a protein-coding gene?",
        "Is MIR22HG a protein-coding gene?",
        "Is CGGBP1 a protein-coding gene?"
    ]
    test_alignment_questions = [
        "Which organism does the DNA sequence come from:CGTACACCATTGGTGCCAGTGACTGTGGTCAATTCGGTAGAAGTAGAGGTAAAAGTGCTGTTCCATGGCTCAGTTGTAGTTATGATGGTGCTAGCAGTTGTTGGAGTTCTGATGACAATGACGGTTTCGTCAGTTG",
        "Which organism does the DNA sequence come from:AGGGGCAGCAAACACCGGGACACACCCATTCGTGCACTAATCAGAAACTTTTTTTTCTCAAATAATTCAAACAATCAAAATTGGTTTTTTCGAGCAAGGTGGGAAATTTTTCGAT", 
    ]
    test_snp_associated_questions = [
        "Which gene is SNP rs1217074595 associated with?",
        "Which gene is SNP rs139642661 associated with?",
        "Which gene is SNP rs1263053296 associated with?",
        "Which gene is SNP rs1391145256 associated with?",
        "Which gene is SNP rs1002944049 associated with?",
        "Which gene is SNP rs962314907 associated with?",
    ]
    ## worm # yeast
    for question in test_alignment_questions:
        response = agent.invoke({"messages": [HumanMessage(content=question)]})
        print("回答结果是：" + response["messages"][-1].content)
        print("-"*100)
        # print(response["messages"][-2].content)
        # print("="*100)
        # print(response["messages"])

    