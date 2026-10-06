import random
import string

# # Ради эксперминета эта функция)
# def create_pass(len):
#     password = ""

#     for i in range(len):
#         password += random.choice(
#             (
#                 random.choice(string.ascii_letters), # английские буквами (a-z, A-Z) 
#                 random.choice(string.digits) # цифры  (0, 9)
#             ) 
#         )

#     return password

# а тут уже классическая
def create_pass(length):
    all_chars = string.ascii_letters + string.digits
    return ''.join(random.choices(all_chars, k=length))


while True:
    try:
        pass_len = int(input("Введите длину пароля: "))
        
        if pass_len <= 0:
            print("Длина пароля должна быть > 0! Попробуйте снова.")
            continue
    
        break
    except ValueError:
        print("Ошибка! Пожалуйста, введите ЦЕЛОЕ ЧИСЛО (например, 8, 12, 16).")

print(f"Ваш готовый пароль: {create_pass(pass_len)}")



