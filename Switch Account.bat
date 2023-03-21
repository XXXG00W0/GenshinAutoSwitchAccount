cd "." 
@rem 若本批处理文件和switch_account.py不在同一路径下，则需要修改双引号里的内容
python "switch_account.py"
timeout /t 5
