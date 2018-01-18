
1.CCF
  代码:
  /wls/appsystem/cp_pic/10
  源目录:
  /nfsc/ccf_core_id406927_vol1004_prd/photo/
  目标目录:
  /facepic/ccf_pic/inpath/10
  定时脚本:copy_files_ip.py
  初始化脚本:cp_10_while.py

2.E模型:
  代码:
   /wls/appsystem/cp_pic/recognition
  源目录:
   /nfsc/opra_fr_id396444_vol1001_prd
  目标目录:
   /facepic/recognition/inpath
  脚本: imLogCopy.py

3.OCR:
  im目录
  代码:
  /wls/appsystem/cp_pic/ocr
  源目录:
  /nfsc/ocr_id_id201211_vol1001_prd/im
  目标目录:
  /facepic/ocr_pic/inpath/im/2017/09
	定时脚本:imCopy.py
	初始化脚本:initImCopy.py

  ocr目录:
  代码:
  /wls/appsystem/cp_pic/ocr
  源目录:
  /nfsc/ocr_id_id201211_vol1001_prd/ocr
  目标目录:
  /facepic/ocr_pic/inpath/ocr
	定时脚本:ocrCopy.py
	初始化脚本:initOcrCopy.py

4.H模型:
  代码目录:
  /wls/appsystem/cp_pic/h_model
  源目录:
  /nfsc/xface_fd_id416020_vol1002_prd
  目标目录:
  /nfsc/xface_fd_id416020_vol1003_prd/h_model/inpath
  脚本:h_model_copy.py




