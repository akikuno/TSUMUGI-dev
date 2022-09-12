from time import sleep
from pathlib import Path
from urllib import request
from urllib.error import URLError
from http.client import RemoteDisconnected
from urllib.error import HTTPError
import math
import pandas as pd

"""
https://www.mousephenotype.org/data/exportraw?phenotyping_center=WTSI&parameter_stable_id=M-G-P_005_001_003&allele_accession_id=MGI:3588650&strain=MGI:2159873&pipeline_stable_id=M-G-P_001&&zygosity=heterozygote&
"""

"""
https://www.mousephenotype.org/data/exportraw?phenotyping_center=UC%20Davis&parameter_stable_id=UCD_OWT_002_001&allele_accession_id=MGI:6152680&strain=MGI:2683688&pipeline_stable_id=UCD_001&&zygosity=heterozygote&
"""

stats = pd.read_csv("data/impc/results/statistical-results-ALL.csv.gz")
"strain" in stats.columns

tmp_stats = stats.copy()
tmp_stats.dropna(subset = ["male_control_count"], inplace=True)

len(stats)
len(tmp_stats)
tmp_stats["phenotyping_center"] = tmp_stats.phenotyping_center.replace(" ", "%20", regex=True)
url = "https://www.mousephenotype.org/data/exportraw?"
tmp_stats["url"] = url + \
            "phenotyping_center=" + tmp_stats["phenotyping_center"] + "&" \
            "parameter_stable_id=" + tmp_stats["parameter_stable_id"] + "&" \
            "allele_accession_id=" + tmp_stats["allele_accession_id"] + "&" \
            "strain=" + tmp_stats["strain_accession_id"] + "&" \
            "pipeline_stable_id=" + tmp_stats["pipeline_stable_id"] + "&" \
            "zygosity=" + tmp_stats["zygosity"] + "&"


output_directry = "data/impc/phenstat"
Path(output_directry).mkdir(parents=True, exist_ok=True)

def task_with_retry(download_url, CONNECTION_RETRY=10):
    save_name="data/impc/phenstat/" + Path(download_url).stem + ".csv"
    if Path(save_name).exists():
        return 0
    for i in range(1, CONNECTION_RETRY + 1):
        try:
            data = request.urlopen(download_url).read()
        except RemoteDisconnected or URLError as e:
            print(f"error:{e} retry:{i}/{CONNECTION_RETRY}")
            sleep(1)
        except HTTPError:
            return 1
        else:
            with open(save_name, mode="wb") as f:
                f.write(data)
            return 0
    print("critical")
    return 2

logfile = Path("data/impc/phenstat/log.csv")
logfile.write_text("")
with open(logfile, "a") as f:
    for idx, download_url in enumerate(tmp_stats["url"].tolist()):
        print(f"No.{idx}, {idx/len(tmp_stats)*100}% finished...")
        if type(download_url) is not str and math.isnan(download_url):
            f.write(f"{idx+1},nan\n")
            continue
        if task_with_retry(download_url) == 0:
            f.write(f"{idx+1},True\n")
        elif task_with_retry(download_url) == 1:
            f.write(f"{idx+1},HTTPError,{download_url}\n")
        elif task_with_retry(download_url) == 2:
            f.write(f"{idx+1},TIMEout,{download_url}\n")
        else :
            f.write(f"{idx+1},Unknown,{download_url}\n")


