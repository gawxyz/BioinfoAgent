import json
import pandas as pd
from langchain_core.messages import HumanMessage
import sys
sys.path.append('../src')
from sub_graph.langchainA import agent

def load_test_cases(json_path):
    """加载测试用例"""
    with open(json_path, 'r') as f:
        test_cases = json.load(f)
    return test_cases

def run_evaluation(test_cases):
    """运行评估并收集结果"""
    results = []
    
    for category, questions in test_cases.items():
        print(f"Evaluating category: {category}")
        
        for question, reference in questions.items():
            print(f"Testing: {question}")
            
            # 调用agent获取回答
            try:
                response = agent.invoke({"messages": [HumanMessage(content=question)]})
                generated_answer = response["messages"][-1].content
            except Exception as e:
                generated_answer = f"Error: {str(e)}"
            
            # 收集结果
            results.append({
                "Category": category,
                "Question": question,
                "Generated Answer": generated_answer,
                "Reference Answer": reference,
                "Needs Review": "Yes"  # 默认需要人工审核
            })
            
    return results

def save_results(results, output_json, output_excel):
    """保存结果到JSON和Excel"""
    # 保存为JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 保存为Excel
    df = pd.DataFrame(results)
    
    # 设置Excel写入选项
    writer = pd.ExcelWriter(output_excel, engine='xlsxwriter')
    
    # 写入数据
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # 获取workbook和worksheet对象
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # 设置单元格格式以支持换行
    wrap_format = workbook.add_format({'text_wrap': True})
    
    # 调整列宽和行高
    for idx, col in enumerate(df.columns):
        # 获取列的最大长度
        max_length = max(
            df[col].astype(str).apply(lambda x: len(x.split('\n')[0])).max(),
            len(col)
        )
        # 设置列宽
        worksheet.set_column(idx, idx, max_length + 2, wrap_format)
    
    # 自动调整行高
    for i in range(len(df)):
        worksheet.set_row(i + 1, None)  # +1 因为标题行占据第一行
    
    # 保存文件
    writer.close()

def main():
    # 加载测试用例
    test_cases = load_test_cases('geneturing.json')
    
    # 运行评估
    results = run_evaluation(test_cases)
    
    # 保存结果
    save_results(results, 'evaluation_results.json', 'evaluation_results.xlsx')
    
    print("Evaluation completed. Results saved to evaluation_results.json and evaluation_results.xlsx")

if __name__ == "__main__":
    main() 