import pandas as pd
import pickle
import uuid
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import openai
import warnings

warnings.filterwarnings("ignore")


path = r'C:\Users\AnGary\Downloads\geckodriver-v0.31.0-win64 (1)\geckodriver.exe'


def driver_init(headless = False):
    if headless:
        fop = Options()
        fop.add_argument('--headless')
        fop.add_argument('--window-size1920x1080')
        return webdriver.Firefox(executable_path = path, options = fop)
    return webdriver.Firefox(executable_path = path)




def openai_key():
    return pickle.load(open('openai_key.p', 'rb'))
    


def chatgpt_request(request):
    openai.api_key = openai_key()
    model_engine = "text-davinci-003"
    packet = openai.Completion.create(
        engine=model_engine,
        prompt=request,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return packet.choices[0].text



#DONT RUN IDIOT 
def create_master_dataset():
    with open(r'C:\Users\AnGary\Documents\pollitical_quiz_raw.txt') as f:
        raw_list = f.readlines()
    raw_list = [rs for rs in raw_list if rs != '\n']
    data = {'id' : [], 'source' : [], 'link' : [], 'status' : []}
    for value in raw_list:
        data['id'].append(str(uuid.uuid4()))
        data['source'].append(value[0:value.find(':')])
        data['link'].append(value[value.find(':') + 2:].replace('\n', ''))
        data['status'].append('uncomplete')
    data = pd.DataFrame(data)
    pickle.dump(data, open('pollitical_master_list.p', 'wb'))



def read_master_dataset():
    return pickle.load(open('pollitical_master_list.p', 'rb'))


def create_pollitical_index_file():
    file = {'strongly agree' : 2, 'agree' : 1, 'netrual' : 0, 'disagree' : -1, 'strongly disagree' : -2}
    pickle.dump(file, open('polltical_index_file.p', 'wb'))



def create_abtirsi_dataset():
    with open(r'C:\Users\AnGary\Documents\Pollitical Quizes\abtirsi.txt') as f:
        raw_list = f.readlines()
    master_dataset = pickle.load(open('pollitical_master_list.p', 'rb'))
    data = {'question_id' : [], 'question' : [], 'stance' : [], 'source' : []}
    for value in raw_list:
        data['question_id'].append(str(uuid.uuid4()))
        data['question'].append(value.replace('\n', '').split('|')[0])
        data['stance'].append(value.replace('\n', '').split('|')[1])
        data['source'].append('abtirsi')
    data = pd.DataFrame(data)
    data['stance'].astype(int)
    return data



def create_quiz_dataset(quiz_name):
    quiz_path = r'C:\Users\AnGary\Documents\Pollitical Quizes\%s.txt' % quiz_name
    with open(quiz_path) as f:
        raw_list = f.readlines()
    data = {'question_id' : [], 'question' : [], 'stance' : [], 'source' : []}
    for value in raw_list:
        data['question_id'].append(str(uuid.uuid4()))
        data['question'].append(value.replace('\n', '').split('|')[0])
        data['stance'].append(value.replace('\n', '').split('|')[1])
        data['source'].append(quiz_name)
    data = pd.DataFrame(data)
    data['stance'].astype(int)
    return data



def create_reference_questions(data, index):
    response_positive = chatgpt_request("Rewrite this in 30 different ways using different keywords and different amounts of words \n %s" % data['question'][index])
    response_positive = [r.split('.')[1].strip() for r in response_positive.split('\n') if r != '']
    new_df = {'question_id' : [], 'question' : [], 'stance' : [], 'source' : []}
    value = int(data['stance'][index])
    if value > 0:
        opposite_value = int('-' + str(value))
    if value < 0:
        opposite_value = value + (int(str(value).replace('-', '')) * 2)
    if value == 0:
        opposite_value = '!'
    if opposite_value != '!':
        response_negative = chatgpt_request("Write the opposite of this in 30 different ways using different keywords and different amounts of words \n %s" % data['question'][index])
        response_negative = [r.split('.')[1].strip() for r in response_negative.split('\n') if r != '']
    for i in range(30):
        new_df['question_id'].append(str(uuid.uuid4()))
        new_df['question'].append(response_positive[i])
        new_df['stance'].append(data['stance'][index])
        new_df['source'].append(df['source'][i] + '.' + 'chatgpt.response-positive')
        if opposite_value != '!':
            new_df['question_id'].append(str(uuid.uuid4()))
            new_df['question'].append(response_negative[i])
            new_df['stance'].append(opposite_value)
            new_df['source'].append(df['source'][i] + '.' + 'chatgpt.response-negative')
    new_df = pd.DataFrame(new_df)
    return data.append(new_df).reset_index().drop(columns = ['index'])
    



def create_questions_dataset(data):
    df = data.copy()
    for i in range(len(data)):
        try:
            print(df['question'][i])
            df = create_reference_questions(df, i)
        except:
            print(df['question'][i] + ' skipped')
        pickle.dump(df, open('questions_dataset_temp_file.p', 'wb'))
    return df


def read_questions_file():
    return pickle.load(open('quiz_question_data.p', 'rb'))
    

def load_questions_file(data):
    try:
        df = pickle.load(open('quiz_question_data.p', 'rb'))
        df = df.reset_index().drop(columns = ['index'])
        pickle.dump(df.append(data), open('quiz_question_data.p', 'wb'))
    except:
        pickle.dump(data, open('quiz_question_data.p', 'wb'))
    


def backup_questions_file():
    pickle.dump(open('quiz_question_data.p', 'rb'), open('quiz_questions_data_backup.p', 'wb'))



    
    







