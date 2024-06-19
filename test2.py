from datetime import datetime, timedelta
import os



def check_date(date_to_check):
    date_to_check = datetime.strptime(date_to_check,'%Y-%m-%d-%H-%M-%S')
    current_date = datetime.now()
    
    if current_date - date_to_check < timedelta(days=1):
        print(f"{current_date} - {date_to_check} < {timedelta(days=1)}")
        return 0
    else: #older than 1 day
        print(f"{current_date} - {date_to_check} >= {timedelta(days=1)}")
        return 1



creation_time = '2024-06-17-14-14-45'

#check_date(creation_time)
path = f"{os.getcwd()}\\backups\\"
for root,dirs,files in os.walk(path):
    for filename in files:
        # if ".backup" in filename:
        #     current_file = filename[-26:-7]
        #     print(current_file)
        #     if check_date(current_file) == 1:
        #         print(f"I will delete {current_file}")
        #         os.remove(f'{path}\\{filename}')
        #         # delete
        if ".rsc" in filename:
            current_file_date = filename[-23:-4]
            print(current_file_date)



#check_date(creation_time)
# 

# check_date = datetime.strptime(creation_time,"%Y-%m-%d")

# current_datetime = datetime.now()

# # Assume date_object is from the previous step

# # Calculate timedelta for 1 day
# one_day = timedelta(days=1)

# # Calculate difference between current datetime and date_object
# difference = current_datetime - check_date
# print(f'Difference {difference}\n Timedelta {timedelta(days=2)}')
# # Compare difference with one_day
# if difference <= one_day:
#     print("The date is 1 day old or less.")
# else:
#     print("The date is more than 1 day old.")