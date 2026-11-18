
import openpyxl

def load_excel_info(file_path,sheet_name):
    wb = openpyxl.load_workbook(file_path)
    #wb.active  加载excel默认打开的sheet表
    sheet = wb[sheet_name] if sheet_name else wb.active

    #最大行数
    max_rows = sheet.max_row

    #最大列数
    max_cols = sheet.max_column
    field_list = []
    for row in range(2, max_rows+1):
        value_list = []
        for col in range(1, max_cols+1):
            value = sheet.cell(row=row, column=col).value
            value_list.append(value)
        field_list.append(value_list)
    return field_list


if __name__ == '__main__':
    file_path = r'D:\学习项目\PythonProject\testcase\1.xlsx'
    sheet_name = '测试集合管理'
    print(load_excel_info(file_path, sheet_name))
