# HHS OCR downloader

Uses GitHub Actions to pull tables of healthcare security breaches reported to the U.S. Department of Health and Human Services Office for Civil Rights. This Python script downloads two CSVs — one for [cases currently under investigation](https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf) and another for archived cases. The script then merges the two CSVs and uploads all three — under investigation, archived and the merged reports — to our FTP server.

I used Selenium and Webdriver Manager to download the CSVs, pandas to clean the data, and Paramiko to upload final CSVs to the server. The action requires environment variables to be stored as the `HOST`, `FTP_USER` and `PASSWORD` secrets in the repository Secrets setting for uploading.

![HHS-OCR workflow](https://user-images.githubusercontent.com/1087467/204594577-676a7e09-5189-41ab-a5dc-c3164c64d3b3.jpeg)
