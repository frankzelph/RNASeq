 #To optimize the parameters for your data, i.e. to obtain the highest number of high quality mapped reads, 
 #you should generate an evaluation data file (cleaned and trimmed FASTQ file from a single sample) that you can use to run through several permutations of bwa, 
#changing a single parameter each time.  You can use the counts script from the gene expression section of this pipeline to see the number and quality of reads mapped with each set of parameters.

import commands
import collections
from itertools import product
# run BWA...
# run dans script...
## use one with best params...


def drange(start, stop, step):
    range_list = []
    r = start
    while r < stop:
        r += step
        range_list.append(r)
    return range_list


def createsample(sample_name):
    cmd = "head -n 10000 {0}.fastq > {0}_head.fastq".format(sample_name)
    commands.getoutput(cmd)
    return "{0}_head.fastq"


def get_params():
    #p = -n, -k,-o, -O, -e, -E
    #d = 0.04, 2, 1, 11, -1, 4
    #all_params = (range(0.04,), range(2), range(1), range(11), range(-1), range(4))
    all_params = product(drange(0.03,0.06, 0.01), range(0,2)) 
    return list(all_params)

def get_bwa(sample_name,index, params):
    #params = zip(["-n","-k","-o","-O","-e","-E"],params)
    params = zip(["-n","-k"],params)
    s = [str(p).strip("()").replace(",","") for p in params]
    params_str = " ".join(s)
    cmd = "bwa aln -t 4 {2}  {1}.fa {0}_head.fastq | bwa samse -r '@RG\\tID:{0}\\tSM:{0}' {1}.fa - {0}_head.fastq > {0}_head.sam".format(sample_name,index,params_str)
    return commands.getoutput(cmd)

#Aligning code to seq

### normal quality
#-n max #diff (int) or missing prob under 0.02 err rate (float) [0.04]
#-k maximum differences in the seed [2]


## These whould need to be changed is RNASeq data is of poor quality
#-O default is high pently to open gap of 11 can also try 7 (to see)
#-o max number of opened gaps (what is this per)
#-E gap extension penaltydefault is 4
#-e number of extension per gap... -1 = 0


def find_best_score(best_score):
    #sort_by_last_diget.and picks lowest one
    best_score.sort(key=lambda x : x[-1], reverse=True)
    print best_score
     return best_score[0][0]

def parse_qualalign(proper_qualalign):
    head = ['Filename', 'Total#Reads', 'NumContigsMatched', 'NumUnaligned', 'NumAligned', 'NumMultiAligned', 'NumSingleAligned', 'NumQualSingles', 'PropQualAligned']
    for line in proper_qualalign.split("\n"):
        res = (line.split("\t"))
        values = map(float,res[1:])
        qual_dic = zip(head[1:],values)
        print head
        print values
        return values
        #print dict(qual_dic)


def main(sample_name, index):
    createsample(sample_name)
    
    quality = []
    #while quality == "poor":
    for param in get_params():
        bwa_out = get_bwa(sample_name, index, param)
        qa = "python countxpression.py 20 20 summarystats.txt {0}_head.sam".format(sample_name)
        proper_qualalign = commands.getoutput(qa)
        param_key =  str(param).strip("()")
        res = parse_qualalign(proper_qualalign)
        print res
        quality.append([param_key] + res)
    best_score = find_best_score(quality)

main("KO", "genome")
