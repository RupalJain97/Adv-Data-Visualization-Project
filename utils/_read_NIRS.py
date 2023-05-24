import pandas as pd

def read_NIRS():
    df = pd.read_csv("/Users/calebjonesshibu/Desktop/tom/pilot/exp_2022_11_22_10/lion/eeg_fnirs_pupil/NIRS.csv",sep = '\t')

    return df.iloc[:,1:20]