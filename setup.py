from setuptools import find_packages, setup

setup(
    name="FMDS",
    version="0.1",
    packages=find_packages(),
    url="",
    license="MIT",
    author="william",
    author_email="",
    description="FastMemeDeliveryService",
    install_requires=[
        "aiofiles==0.6.0",
        "fastapi>=0.65.0,<0.66.0",
        "mysqlclient>=2.0.3,<2.1.0",
        "passlib>=1.7.4,<1.8.0",
        "python-dotenv==0.17.1",
        "python-magic>=0.4.18,<0.5.0",
        "python-multipart==0.0.5",
        "python-jose[cryptography]>=3.2.0,<4.0.0",
        # "sqlalchemy>=1.3.23,<1.4.0",
        "sqlalchemy>=1.4.0,<1.5.0",
        "timeflake>=0.4.0,<0.5.0",
        "uvicorn[standard]>=0.13.0,<0.14.0",
    ],
)
