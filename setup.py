from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pricepulse",
    version="0.1.0",
    description="Python client for PricePulse - real-time price monitoring API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PricePulse Team",
    author_email="pricepulse@dev",
    url="https://github.com/rock2089/pricepulse-api",
    packages=find_packages(),
    install_requires=["requests>=2.25.0"],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Office/Business :: Financial",
    ],
    keywords="price monitoring ecommerce carousell amazon singapore arbitrage",
)
