from Bio.Blast import NCBIWWW
from Bio import SeqIO
import time

def blastn(sequence: str) -> str:
    """
    使用BLASTN进行DNA序列对DNA数据库的比对
    
    Args:
        sequence (str): 输入的DNA序列
        
    Returns:
        str: BLAST比对结果
    """
    try:
        print("正在执行BLASTN比对...")
        result_handle = NCBIWWW.qblast(
            program="blastn",
            database="nt",  # 核酸数据库
            sequence=sequence,
            expect=1e-10,
            hitlist_size=10,
            megablast=True  # 使用MegaBLAST算法加速搜索
        )
        blast_results = result_handle.read()
        result_handle.close()
        return blast_results
    except Exception as e:
        return f"BLASTN比对出错: {str(e)}"

def blastp(sequence: str) -> str:
    """
    使用BLASTP进行蛋白质序列对蛋白质数据库的比对
    
    Args:
        sequence (str): 输入的蛋白质序列
        
    Returns:
        str: BLAST比对结果
    """
    try:
        print("正在执行BLASTP比对...")
        result_handle = NCBIWWW.qblast(
            program="blastp",
            database="nr",  # 蛋白质数据库
            sequence=sequence,
            expect=1e-10,
            hitlist_size=10,
            matrix="BLOSUM62"  # 使用BLOSUM62打分矩阵
        )
        blast_results = result_handle.read()
        result_handle.close()
        return blast_results
    except Exception as e:
        return f"BLASTP比对出错: {str(e)}"

def blastx(sequence: str) -> str:
    """
    使用BLASTX进行DNA序列(翻译后)对蛋白质数据库的比对
    
    Args:
        sequence (str): 输入的DNA序列
        
    Returns:
        str: BLAST比对结果
    """
    try:
        print("正在执行BLASTX比对...")
        result_handle = NCBIWWW.qblast(
            program="blastx",
            database="nr",  # 蛋白质数据库
            sequence=sequence,
            expect=1e-10,
            hitlist_size=10,
            genetic_code=1  # 使用标准遗传密码
        )
        blast_results = result_handle.read()
        result_handle.close()
        return blast_results
    except Exception as e:
        return f"BLASTX比对出错: {str(e)}"

def tblastn(sequence: str) -> str:
    """
    使用TBLASTN进行蛋白质序列对DNA数据库(翻译后)的比对
    
    Args:
        sequence (str): 输入的蛋白质序列
        
    Returns:
        str: BLAST比对结果
    """
    try:
        print("正在执行TBLASTN比对...")
        result_handle = NCBIWWW.qblast(
            program="tblastn",
            database="nt",  # 核酸数据库
            sequence=sequence,
            expect=1e-10,
            hitlist_size=10,
            genetic_code=1  # 使用标准遗传密码
        )
        blast_results = result_handle.read()
        result_handle.close()
        return blast_results
    except Exception as e:
        return f"TBLASTN比对出错: {str(e)}"

def parse_fasta_and_blast(fasta_file: str, blast_type: str) -> dict:
    """
    读取FASTA文件并根据指定类型进行BLAST比对
    
    Args:
        fasta_file (str): FASTA文件路径
        blast_type (str): BLAST类型 ('blastn', 'blastp', 'blastx', 'tblastn')
        
    Returns:
        dict: 序列ID到BLAST结果的映射
    """
    # BLAST函数映射
    blast_functions = {
        'blastn': blastn,
        'blastp': blastp,
        'blastx': blastx,
        'tblastn': tblastn
    }
    
    if blast_type not in blast_functions:
        raise ValueError(f"不支持的BLAST类型: {blast_type}")
        
    results = {}
    blast_func = blast_functions[blast_type]
    
    # 读取FASTA文件并执行BLAST
    for record in SeqIO.parse(fasta_file, "fasta"):
        print(f"\n处理序列: {record.id}")
        blast_result = blast_func(str(record.seq))
        results[record.id] = blast_result
        time.sleep(5)  # 避免过于频繁请求NCBI服务器
        
    return results

# 使用示例
if __name__ == "__main__":
    # DNA序列BLASTN示例
    dna_seq = "AGGGGCAGCAAACACCGGGACACACCCATTCGTGCACTAATCAGAAACTTTTTTTTCTCAAATAATTC"
    blastn_result = blastn(dna_seq)
    print("BLASTN结果:", blastn_result)
    
    # 蛋白质序列BLASTP示例
    protein_seq = "MAEGEITTFTALTEKFNLPPGNYKKPKLLYCSNGGHFLRILPDGTVDGTRDRSDQHIQLQLSAESVGEVYIKSTETGQYLAMDTDGLLYGSQTPNEECLFLERLEENHYNTYISKKHAEKNWFVGLKKNGSCKRGPRTHYGQKAILFLPLPV"
    blastp_result = blastp(protein_seq)
    print("BLASTP结果:", blastp_result)
    
    # DNA序列BLASTX示例
    blastx_result = blastx(dna_seq)
    print("BLASTX结果:", blastx_result)
    
    # 蛋白质序列TBLASTN示例
    tblastn_result = tblastn(protein_seq)
    print("TBLASTN结果:", tblastn_result)
    
    # FASTA文件批量BLAST示例
    # results = parse_fasta_and_blast("sequences.fasta", "blastn")