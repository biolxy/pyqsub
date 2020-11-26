#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
File Name   : pyqsub.py .

Author      : biolxy
E-mail      : biolxy@aliyun.com
Created Time: 2020-10-15 16:48:08
version     : 1.0
Function    : The author is too lazy to write nothing
Usage       :
"""
import enum
import sys
import os
import stat
import argparse
__VERSION__ = '1.0.0'


class QsubCmd(object):
    """
        len(cmdlist) must == len(cmdthread)
        cmdlist = [
            [cmd1],
            [cmd2],
            [cmd3_1, cmd3_2],
            [cmd4]
        ]
        cmdthread = [
            16,
            1,
            1,
            1
        ]
    """
    def __init__(self, qsubfile, cmdlist, cmdthread):
        self.qsubfile = qsubfile
        self.cmdlist = cmdlist
        self.cmdthread = cmdthread
        self.qsubfilePath = os.path.dirname(self.qsubfile)
        self.fnline = []
        self.head = True
        self.depend = ""
        self.jobn = 0

    def __chmod_qsubfile(self):
        if os.path.isfile(self.qsubfile):
            # 777
            os.chmod(self.qsubfile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    def __add_fnline(self, cmdl):
        for x, cmd in enumerate(cmdl):
            self.jobname = "step" + str(self.jobn+1) + "_" + str(x+1)
            self.logfile = os.path.join(self.qsubfilePath, self.jobname + ".log")
            if self.head:
                self.depend = ""
            else:
                self.depend = "-W depend=afterok${latest_job}"
            ProcessingCores = self.cmdthread[self.jobn]
            line = "current_job_id=$( qsub -N {jobname} -o {logfile}.stdout -e {logfile}.stderr -l nodes=1:ppn={ProcessingCores} -q high {depend} <<<'{cmd}' )\necho ${{current_job_id}}\njob_ids=\"${{job_ids}}:${{current_job_id}}\"\n".format(
                        jobname=self.jobname,
                        logfile=self.logfile,
                        ProcessingCores=ProcessingCores,
                        cmd=cmd,
                        depend=self.depend)
            self.fnline.append(line)
        self.head = False

    def __getfnline(self):
        for cmdl in self.cmdlist:
            self.__add_fnline(cmdl)
            self.jobn += 1
            line = "latest_job=\"${job_ids}\"\n"
            self.fnline.append(line)

    def __writefn(self):
        with open(self.qsubfile, 'w') as ff:
            ff.writelines(self.fnline)
    
    def return_qsubfile(self):
        self.__getfnline()
        self.__writefn()
        self.__chmod_qsubfile()
        return self.qsubfile


def getQsubScript(qsubcmd_list, qsubfile, ProcessingCores_list):
    fn = open(qsubfile, 'w')
    job_number = 0
    if len(qsubcmd_list) != 0:
        for x, cmd in enumerate(qsubcmd_list):
            ProcessingCores = ProcessingCores_list[x]
            if len(cmd) == 1:
                cmd = cmd[0]
                jobname = str(x) + "_" + str(0)
                logfile = os.path.dirname(qsubfile) + "/" + jobname + ".log"
                if job_number == 0:
                    depend = ""
                else:
                    depend = "-W depend=afterok${{job_ids}}".format()
                job_number += 1
                # print(job_number)
                line1 = "current_job_id=$( qsub -N {jobname} -o {logfile}.stdout -e {logfile}.stderr -l nodes=1:ppn={ProcessingCores} -q high {depend} <<<'{cmd}' )\necho ${{current_job_id}}\njob_ids=\"${{job_ids}}:${{current_job_id}}\"".format(
                    jobname=jobname,
                    logfile=logfile,
                    ProcessingCores=ProcessingCores,
                    cmd=cmd,
                    depend=depend)

                # print(line1)
                fn.write("{}\n".format(line1))
            elif len(cmd) >= 1:
                job_number += 1
                line1 = "latest_job_is=\"${{job_ids}}\"".format()
                fn.write("{}\n".format(line1))
                number = 0
                for xx, cmd_i in enumerate(cmd):
                    jobname = str(x) + "_" + str(xx)
                    jobname = jobname + "_" + str(number)
                    number += 1
                    logfile = os.path.dirname(qsubfile) + "/" + jobname + ".log"
                    line1 = "current_job_id=$( qsub -N {jobname} -o {logfile}.stdout -e {logfile}.stderr -l nodes=1:ppn={ProcessingCores} -q high -W depend=afterok$latest_job_is  <<<'{cmd}' )\necho ${{current_job_id}}\njob_ids=\"${{job_ids}}:${{current_job_id}}\"".format(
                        jobname=jobname,
                        logfile=logfile,
                        ProcessingCores=ProcessingCores,
                        cmd=cmd_i)
                    # print(line1)
                    fn.write("{}\n".format(line1))
    else:
        pass
    fn.close()
    # mode:777
    os.chmod(qsubfile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    return qsubfile


def mkdirtd(indir):
    if not os.path.exists(indir):
        os.mkdir(indir)
        # 777
        os.chmod(indir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


def get_cmd(infile):
    res = []
    with open(infile, 'r') as ff:
        for line in ff:
            line = line.strip()
            res.append(line)
    return res


def main():
    # print("pyqsub")
    # print(qsubfile)
    cmdlist2 = [os.path.abspath(x) for x in cmdlist]
    cmdlist3 = [get_cmd(x) for x in cmdlist2]
    # print(cmdlist3)
    # print(cmdthread)
    # getQsubScript(cmdlist3, qsubfile, cmdthread)
    qsub = QsubCmd(qsubfile, cmdlist3, cmdthread)
    qq = qsub.return_qsubfile()
    print(qq)


if __name__ == '__main__':
    try:
        SCRIPT_FOLDER = os.path.abspath(os.path.dirname(__file__))
        parser = argparse.ArgumentParser(prog="pyqsub {}".format(__VERSION__),
                                         description="get .qsub cmd")
        parser.add_argument('-o',
                            '--outputfile',
                            type=str,
                            help="the specify output .qsub file",
                            required=True)
        parser.add_argument('-c', '--cmdfile', nargs="+", required=True)
        parser.add_argument('-n',
                            '--cmdthread',
                            nargs="+",
                            type=int,
                            required=True)
        args = parser.parse_args()
        qsubfile = os.path.abspath(args.outputfile)
        cmdlist = args.cmdfile
        cmdthread = args.cmdthread
        # print(args.cmdfile)
        main()
    except Exception:
        raise