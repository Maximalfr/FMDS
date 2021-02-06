from setuptools import find_packages, setup

setup(
    name="FMDS",
    version="0.1",
    packages=find_packages("app"),
    url="",
    license="MIT",
    author="william",
    author_email="",
    description="FastMemeDeliveryService",
    install_requires=[
        "aiofiles==0.6.0",
        "fastapi>=0.63.0,<0.64.0",
        "python-dotenv==0.15.0",
        "python-magic>=0.4.18,<0.5.0",
        "python-multipart==0.0.5",
        "sqlalchemy>=1.3.23,<1.4.0",
        "timeflake>=0.3.3,<0.4.0",
        "uvicorn[standard]>=0.13.0,<0.14.0",
    ],
)
