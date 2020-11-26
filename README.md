### pyqsub
#### uasge
```shell
usage: pyqsub 1.0.0 [-h] -o OUTPUTFILE -c CMDFILE [CMDFILE ...] -n CMDTHREAD
                    [CMDTHREAD ...]

get .qsub cmd

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        the specify output .qsub file
  -c CMDFILE [CMDFILE ...], --cmdfile CMDFILE [CMDFILE ...]
  -n CMDTHREAD [CMDTHREAD ...], --cmdthread CMDTHREAD [CMDTHREAD ...]
```

example:
```shell
python /data/home/lixiangyong/project/pyqsub/pyqsub.py -c "${output}"/step1.cmd "${output}"/step2.cmd "${output}"/step3.cmd "${output}"/step4.cmd "${output}"/step5.cmd  -n 32 1 1 1 1 -o "${output}"/cmd.qsub
```