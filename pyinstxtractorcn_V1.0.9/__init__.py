from .cli import (
    PyInstExtractorError,
    InvalidFileError,
    ExtractionError,
    dcp as _dcp
)

__version__ = "1.0.7"
__all__ = ["dcp", "PyInstExtractorError", "InvalidFileError", "ExtractionError"]

def dcp(file_path: str, output_dir: str = None) -> str:
    r"""
    解包PyInstaller生成的可执行文件
    
    :param file_path: 目标文件路径（支持格式：C:/path、C:\\path、相对路径）
    :param output_dir: 自定义输出目录（支持格式：C:\\output、./output、/tmp/output）
    :return: 解包目录绝对路径
    :raises: 
        InvalidFileError - 输入文件无效时抛出
        ExtractionError - 解包过程失败时抛出
    """
    try:
        return _dcp(file_path, output_dir)
    except PyInstExtractorError as e:
        raise e

if __name__ == "__main__":
    from .cli import main
    main()