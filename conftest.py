import subprocess

def pytest_sessionfinish(session, exitstatus):
    print("\n======>>> pytest_sessionfinish 钩子触发，准备生成allure报告")
    allure_bat = r"D:\pycharm\allure-2.38.0\bin\allure.bat"
    work_dir = r"D:\学习项目\PythonProject"
    try:
        cmd = [
            allure_bat,
            "generate",
            "allure-results",
            "-o",
            "report",
            "--clean"
        ]
        ret = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True
        )
        print("执行命令：", " ".join(cmd))
        print("stdout:\n", ret.stdout)
        print("stderr:\n", ret.stderr)
        if ret.returncode == 0:
            print("✅ 报告生成成功，正在打开报告页面")
            subprocess.run([allure_bat, "open", "report"], cwd=work_dir)
        else:
            print(f"❌ generate 失败，返回码：{ret.returncode}")
    except Exception as e:
        print("❌ 执行allure命令异常：", str(e))
