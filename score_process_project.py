
def value_input():
    name=input("이름:")
    kor = int(input('국어 : '))
    eng= int(input('영어 : '))
    math = int(input('수학 : '))
    all_score=kor+eng+math
    avg=(kor+eng+math)/3
    with open("score.txt","a") as file:
        file.write(name)
        file.write("\t")
        file.write(str(kor))
        file.write("\t")
        file.write(str(eng))
        file.write("\t")
        file.write(str(math))
        file.write("\t")
        file.write(str(all_score))
        file.write("\t")
        file.write(str(avg))
        file.write("\n")


def read_list():
    score_list = []
    with open("score.txt","r") as file:
        line = None
        while line != '':
            line = file.readline()
            one_list = line.split("\t")
            one_list[-1] = one_list[-1][:-1]
            one_list[1:] = list(map(float,one_list[1:]))
            score_list.append(one_list)
    score_list = score_list[:-1]
    return score_list

def read_all():
    score_list = read_list()
    print("이름\t국어  영어  수학  총점  평균")
    for i in score_list:
        print(i)

def search_name():
    name=input('\n검색할 이름을 입력하세요 : ')
    score_list = read_list()
    for i in range (len(score_list)):
        if score_list[i][0] == name:
            print(score_list[i])
def search_avg():
    avg_score=int(input('\n검색할 평균 점수를 입력하세요 : '))
    score_list = read_list()
    score_list = sorted(score_list, key=lambda x: x[-1], reverse=True)
    for i in range (len(score_list)):
        if score_list[i][-1] >= avg_score:
            print(score_list[i])
    

def update_list(new_list):
        with open("score.txt","w") as file:
            for i in range(len(new_list)):
                file.write(new_list[i][0])
                file.write("\t")
                file.write(str(new_list[i][1]))
                file.write("\t")
                file.write(str(new_list[i][2]))
                file.write("\t")
                file.write(str(new_list[i][3]))
                file.write("\t")
                file.write(str(new_list[i][4]))
                file.write("\t")
                file.write(str(new_list[i][5]))
                file.write("\n")

def del_info():
    name=input('\n삭제할 사람의 이름을 입력하세요 : ')
    score_list = read_list()
    new_list=[]
    for i in range (len(score_list)):
        if score_list[i][0] != name:
            new_list.append(score_list[i])
    update_list(new_list)


def update_score():
    name=input('\n 성적을 변경 할 사람의 이름을 입력하세요 : ')    
    score_list = read_list()
    new_list=[]
    for i in range (len(score_list)):
        if score_list[i][0] != name:
            new_list.append(score_list[i])
        else:
            kor = int(input('국어 : '))
            eng= int(input('영어 : '))
            math = int(input('수학 : '))
            score_list[i][1]=kor
            score_list[i][2]=eng
            score_list[i][3]=math
            score_list[i][4]=kor+eng+math
            score_list[i][5]=((kor+eng+math)/3)
            new_list.append(score_list[i])
    update_list(new_list)

def score_process():
    while True:
        menu = int(input('\n<성적 처리 프로그램> \n1. 새로운 정보 입력, 2. 전체 출력 3. 사람 정보 검색 \n4.평균 이상 정보 검색, 5.정보 삭제 6.성적 변경 0.종료 \n 입력값 : '))
        if menu == 1:
            value_input()
        elif menu==2:
            read_all()
        elif menu == 3:
            search_name()
        elif menu == 4:
            search_avg()
        elif menu==5:
            del_info()
        elif menu == 6:
            update_score()
        else:
            break
score_process()
