from vfs_bot import VFSBot
from config import CHECK_INTERVAL
import time

def main():
    bot = VFSBot()
    
    try:
        print("Bot başlatıldı. Manuel olarak giriş yapınız...")
        input("Giriş yaptıktan sonra ENTER tuşuna basınız...")
        
        while True:
            print("\nRandevu kontrolü yapılıyor...")
            
            if bot.check_availability():
                # Randevu bulunduğunda yapılacak işlemler
                print("Randevu bulundu! Program sonlandırılıyor...")
                break
            
            print(f"{CHECK_INTERVAL/60} dakika sonra tekrar kontrol edilecek...")
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından sonlandırıldı.")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
