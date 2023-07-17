import pandas as pd
files_csv_name = './app/connect_csv/files.csv'


def read_df(csv_name):
    df = pd.read_csv(csv_name, sep = ",")
    return df


def write_df(csv_name, data):
    df = pd.DataFrame(data)
    df.to_csv(csv_name, mode='a', header=False, index=False)


def take_last_parametr(csv_name, parametr):
    df = read_df(csv_name)
    return int(df[parametr].iloc[-1])


def get_all_files(csv_name):
    df = pd.read_csv(csv_name, sep = ",")
    return df.to_dict('records')


def find_file(csv_name, id):
    df = pd.read_csv(csv_name, sep = ",")
    if len((df[df["file_id"] == id ].values)) == 0 :
        return  False
    data ={
        'file_id': (df[df["file_id"] == id ]['file_id'].values[0]),
        'file_name': (df[df["file_id"] == id ]['file_name'].values[0]),
        'file_path': (df[df["file_id"] == id ]['file_path'].values[0])
    }
    return data


def delete_df(csv_file, id):
    df = pd.read_csv(csv_file, sep = ",")
    df = df[df.file_id != id]
    df.to_csv(files_csv_name, mode='w', index=False)
