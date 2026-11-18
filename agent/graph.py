"""
思路：
1、解析上传的md文件,获取接口参数
2、根据大模型，将接口进行分组，并生成测试用例
3、将测试用例，写入excel文档中
4、执行测试用例
"""
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent.node.generate_test_cases import generate_test_cases
from agent.node.parse_md_file import parse_md_file
from agent.node.run_test_cases import run_test_cases
from agent.node.write_to_excel import write_to_excel
from agent.state import ApiState

api_graph =StateGraph(ApiState)

#定义节点
api_graph.add_node('parse_md_file',parse_md_file)
api_graph.add_node('write_to_excel',write_to_excel)
api_graph.add_node('generate_test_cases',generate_test_cases)
api_graph.add_node('run_test_cases',run_test_cases)


#添加边
api_graph.add_edge(START,'parse_md_file')
api_graph.add_edge('parse_md_file','generate_test_cases')
api_graph.add_edge('generate_test_cases','write_to_excel')
api_graph.add_edge('write_to_excel','run_test_cases')
api_graph.add_edge('run_test_cases',END)


#绘制图
app = api_graph.compile()


#打印图
print(app.get_graph().print_ascii())

