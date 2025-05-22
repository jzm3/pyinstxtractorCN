PyInstxtractorCN (v1.0.9) 中文文档
=================================

项目仓库
========
源代码和最新版本请访问 GitHub：
https://github.com/jzm3/pyinstxtractorCN

概述
====
本工具是针对 PyInstaller 6.12.0 及更低版本生成的 Windows 可执行文件（.exe）的解包工具汉化版，支持提取以下内容：
- Python 字节码文件（.pyc）
- 资源文件（图片/配置文件等）
- 依赖库文件
- PYZ 压缩包内容

功能特性
========
- 全版本兼容：支持 PyInstaller 2.0 至 6.x 打包的文件
- 智能解压：自动处理 Zlib 压缩数据，保留加密文件原始内容
- 字节码修复：自动修复提取的 .pyc 文件头（适配 uncompyle6/decompyle3）
- 安全防护：自动过滤非法路径字符（示例：恶意/../路径 → 恶意__路径）
- 中文日志：完整汉化的错误提示和进度信息
- 自定义输出路径：支持指定任意解包目录，自动创建不存在的路径

安装方式
========
通过 PyPI 安装：
    pip install pyinstxtractorcn

手动运行：
1. 克隆仓库：
    git clone https://github.com/jzm3/pyinstxtractorCN.git
2. 执行解包：
    python pyinstxtractorCN/cli.py <目标文件.exe>

使用示例
========
基础命令：
    pyinstxtractorcn 目标文件.exe

Python 调用：
    import pyinstxtractorcn
    pyinstxtractorcn.dcp('目标文件.exe')

高级用法：
    控制台：
        # Windows 指定绝对路径
        pyinstxtractorcn 目标文件.exe --output "C:\\分析结果\\output"

        # Linux/Mac 指定绝对路径
        pyinstxtractorcn 目标文件.exe --output "/home/user/分析结果"

        # 使用相对路径
        pyinstxtractorcn 目标文件.exe --output "./output"
    
    Python 调用：
        # Windows 路径（原始字符串）
        pyinstxtractorcn.dcp(r'C:\测试文件\目标文件.exe', output_dir=r'C:\分析结果\output')

        # 跨平台路径（正斜杠）
        pyinstxtractorcn.dcp('/tmp/测试文件/目标文件.exe', output_dir='/tmp/output')

        # 带空格的路径处理
        pyinstxtractorcn.dcp(r'C:\My Documents\测试文件.exe', output_dir=r'C:\分析结果\output')

反编译建议：
推荐工具组合：
- uncompyle6（Python 3.8 以下）：https://pypi.org/project/uncompyle6/
- decompyle3（Python 3.9+）：https://pypi.org/project/decompyle3/
- pycdc（跨版本反编译器）：https://github.com/zrax/pycdc

注意事项
========
1. 版本匹配：建议使用与打包环境相同的 Python 版本运行本工具（支持 Python 3.6+）
2. 加密处理：
   - 加密内容将保存为 .encrypted 文件
   - 若出现 marshal.load 错误，请检查文件完整性
3. 路径规范：
   - 空文件名会自动生成 UUID（如 9b4a8f2c.pyc）
   - 自动转换非法路径字符（示例：恶意/../路径 → 恶意__路径）

技术支持
========
问题反馈渠道：
- 开发者邮箱：
  pyinstxtractorcn@outlook.com
  pyinstxtractorcn@163.com
- 提交 GitHub Issue：
  https://github.com/jzm3/pyinstxtractorCN/issues

开源协议
========
本项目采用 GNU General Public License v3.0
完整协议文本请查看：
https://github.com/jzm3/pyinstxtractorCN/blob/main/LICENSE

【警告】
本工具仅限用于：
- 软件逆向工程研究
- 合法授权的安全审计
- 学术用途

禁止用于任何形式的商业破解或非法用途！使用者需自行承担法律责任。


PyInstxtractorCN (v1.0.9) English document
=========================

A Chinese-localized unpacking tool for PyInstaller-generated Windows executables. 
Supports files built with PyInstaller 6.12.0 and earlier versions.

Project Repository
==================
GitHub: https://github.com/jzm3/pyinstxtractorCN

Features
========
- Full version compatibility (PyInstaller 2.0-6.x)
- Smart extraction with Zlib decompression
- Automatic .pyc header repair (compatible with uncompyle6/decompyle3)
- Path sanitization (e.g., "malicious/../path" → "malicious__path")
- Chinese localization (logs and prompts)
- Custom output path: Supports specifying any extraction directory with auto-creation

Installation
============
Via PyPI:
    pip install pyinstxtractorcn

Manual Execution:
1. Clone repository:
    git clone https://github.com/jzm3/pyinstxtractorCN.git
2. Run unpacker:
    python pyinstxtractorCN/cli.py <target.exe>

Usage Examples
==============
Basic command:
    pyinstxtractorcn target.exe

Python API:
    import pyinstxtractorcn
    pyinstxtractorcn.dcp('target.exe')

Advanced usage:
    Console:
        # Windows absolute path
        pyinstxtractorcn target.exe --output "C:\\analysis\\output"

        # Linux/Mac absolute path
        pyinstxtractorcn target.exe --output "/home/user/analysis"

        # Relative path
        pyinstxtractorcn target.exe --output "./output"
    
    Python call:
        # Windows path (raw string)
        pyinstxtractorcn.dcp(r'C:\test_files\target.exe', output_dir=r'C:\analysis\output')

        # Cross-platform path (forward slashes)
        pyinstxtractorcn.dcp('/tmp/test_files/target.exe', output_dir='/tmp/output')

        # Handle paths with spaces
        pyinstxtractorcn.dcp(r'C:\My Documents\target.exe', output_dir=r'C:\analysis\output')

Output Structure
================
sample.exe_extracted/
├── PYZ-00.pyz_extracted/    # Dependency bytecode
├── pyiboot01_bootstrap/     # Bootloader files
├── _pytransform.dll         # Encryption module (if present)
├── runtime/                 # Runtime dependencies
└── sample.pyc               # Main program bytecode

Decompilation Tools
===================
- uncompyle6 (Python <3.8): https://pypi.org/project/uncompyle6/
- decompyle3 (Python ≥3.9): https://pypi.org/project/decompyle3/
- pycdc (Cross-version): https://github.com/zrax/pycdc

Important Notes
===============
1. Python Version Matching
   - Recommended to use same Python version as packing environment
   - Supports Python 3.6+ runtime

2. Encrypted Files
   - Encrypted content saved as .encrypted files
   - Verify file integrity if marshal.load errors occur

3. Path Handling
   - Auto-generate UUID for empty filenames (e.g., 9b4a8f2c.pyc)
   - Sanitize illegal path characters

Technical Support
=================
Contact:
- Email: pyinstxtractorcn@outlook.com / pyinstxtractorcn@163.com
- GitHub Issues: https://github.com/jzm3/pyinstxtractorCN/issues

License
=======
GNU General Public License v3.0
Full text: https://github.com/jzm3/pyinstxtractorCN/blob/main/LICENSE

WARNING
=======
This tool is strictly for:
- Reverse engineering research
- Legally authorized security audits
- Academic purposes

Commercial cracking and illegal uses are prohibited. Users assume full legal responsibility.