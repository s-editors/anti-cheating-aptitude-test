import mysql.connector
import re

# DB Config
config = {
    'user': 'root',
    'password': 'suyash2005',
    'host': 'localhost',
    'database': 'aptitude_test_db'
}

raw_data = """
Q1. Capital of India is: 
A) Mumbai 
B) New Delhi 
C) Kolkata 
D) Chennai 
✅ Ans: B 

Q2. National animal of India: 
A) Lion 
B) Elephant 
C) Tiger 
D) Leopard 
✅ Ans: C 

Q3. Who is known as the Father of the Nation (India)? 
A) Jawaharlal Nehru 
B) Subhash Chandra Bose 
C) Mahatma Gandhi 
D) B. R. Ambedkar 
✅ Ans: C 

Q4. Largest continent in the world: 
A) Africa 
B) Europe 
C) Asia 
D) Australia 
✅ Ans: C 

Q5. Indian currency is issued by: 
A) SBI 
B) RBI 
C) SEBI 
D) Finance Ministry 
✅ Ans: B 

Q6. National bird of India: 
A) Peacock 
B) Eagle 
C) Sparrow 
D) Parrot 
✅ Ans: A 

Q7. Taj Mahal is located in: 
A) Delhi 
B) Jaipur 
C) Agra 
D) Lucknow 
✅ Ans: C 

Q8. Largest ocean in the world: 
A) Atlantic 
B) Indian 
C) Arctic 
D) Pacific 
✅ Ans: D 

Q9. Who wrote the Indian National Anthem? 
A) Bankim Chandra 
B) Rabindranath Tagore 
C) Sarojini Naidu 
D) Subhash Bose 
✅ Ans: B 

Q10. First President of India: 
A) Nehru 
B) Rajendra Prasad 
C) Radhakrishnan 
D) Patel 
✅ Ans: B 

Q11. CPU stands for: 
A) Central Programming Unit 
B) Central Processing Unit 
C) Computer Processing Unit 
D) Central Power Unit 
✅ Ans: B 

Q12. Which of the following is an input device? 
A) Monitor 
B) Printer 
C) Keyboard 
D) Speaker 
✅ Ans: C 

Q13. Which is NOT an operating system? 
A) Windows 
B) Linux 
C) Android 
D) MS Word 
✅ Ans: D 

Q14. RAM is a type of: 
A) Software 
B) Hardware 
C) Virus 
D) Compiler 
✅ Ans: B 

Q15. Full form of ROM: 
A) Read Only Memory 
B) Random Only Memory 
C) Read Once Memory 
D) Run Only Memory 
✅ Ans: A 

Q16. Which device displays output? 
A) Mouse 
B) Keyboard 
C) Monitor 
D) Scanner 
✅ Ans: C 

Q17. Which one is secondary storage? 
A) RAM 
B) Cache 
C) Hard Disk 
D) Register 
✅ Ans: C 

Q18. 1 KB = ? Bytes 
A) 100 
B) 512 
C) 1000 
D) 1024 
✅ Ans: D 

Q19. Which software is used for word processing? 
A) MS Excel 
B) MS Word 
C) MS Paint 
D) Notepad 
✅ Ans: B 

Q20. Which key is used to delete text? 
A) Shift 
B) Enter 
C) Delete 
D) Ctrl 
✅ Ans: C 

Q21. Internet is a: 
A) LAN 
B) MAN 
C) WAN 
D) PAN 
✅ Ans: C 

Q22. WWW stands for: 
A) World Wide Web 
B) World Web Wide 
C) Web World Wide 
D) Wide World Web 
✅ Ans: A 

Q23. Which protocol is used for web browsing? 
A) FTP 
B) SMTP 
C) HTTP 
D) POP 
✅ Ans: C 

Q24. Which of the following is a web browser? 
A) Google 
B) Chrome 
C) Yahoo 
D) Gmail 
✅ Ans: B 

Q25. E-mail is sent using: 
A) HTTP 
B) FTP 
C) SMTP 
D) POP 
✅ Ans: C 

Q26. Which is a search engine? 
A) Facebook 
B) Gmail 
C) Google 
D) WhatsApp 
✅ Ans: C 

Q27. Cloud storage example: 
A) Pen drive 
B) Hard disk 
C) Google Drive 
D) CD 
✅ Ans: C 

Q28. URL stands for: 
A) Uniform Resource Locator 
B) Universal Resource Link 
C) Uniform Resource Link 
D) Universal Remote Locator 
✅ Ans: A 

Q29. Which is NOT a social media platform? 
A) Instagram 
B) Twitter 
C) WhatsApp 
D) Wikipedia 
✅ Ans: D 

Q30. Which technology is used for online payments? 
A) GPS 
B) UPI 
C) LAN 
D) USB 
✅ Ans: B 

Q31. HTML is used for: 
A) Programming 
B) Styling 
C) Structuring web pages 
D) Database 
✅ Ans: C 

Q32. CSS is used for: 
A) Logic 
B) Database 
C) Styling 
D) Hosting 
✅ Ans: C 

Q33. JavaScript is mainly used for: 
A) Styling 
B) Interactivity 
C) Database 
D) Hardware 
✅ Ans: B 

Q34. Which language is used for backend development? 
A) HTML 
B) CSS 
C) Python 
D) XML 
✅ Ans: C 

Q35. Which is NOT a programming language? 
A) Java 
B) Python 
C) HTML 
D) C++ 
✅ Ans: C 

Q36. SQL is used for: 
A) Designing 
B) Styling 
C) Database queries 
D) Networking 
✅ Ans: C 

Q37. Which database is relational? 
A) MongoDB 
B) MySQL 
C) Redis 
D) Cassandra 
✅ Ans: B 

Q38. Which symbol is used for comments in Python? 
A) // 
B) <!-- --> 
C) # 
D) ** 
✅ Ans: C 

Q39. Which is an IDE? 
A) Chrome 
B) VS Code 
C) Windows 
D) Linux 
✅ Ans: B 

Q40. Which OS is open-source? 
A) Windows 
B) macOS 
C) Linux 
D) DOS 
✅ Ans: C 

Q41. What does AI stand for? 
A) Automatic Intelligence 
B) Artificial Intelligence 
C) Advanced Internet 
D) Applied Information 
✅ Ans: B 

Q42. Which is used to store temporary data? 
A) ROM 
B) Hard Disk 
C) RAM 
D) DVD 
✅ Ans: C 

Q43. Which device connects networks? 
A) Switch 
B) Router 
C) Hub 
D) Modem 
✅ Ans: B 

Q44. Virus is a type of: 
A) Hardware 
B) Software 
C) Malware 
D) Firmware 
✅ Ans: C 

Q45. Which file extension is for Python? 
A) .java 
B) .html 
C) .py 
D) .js 
✅ Ans: C 

Q46. Which is NOT a database? 
A) MySQL 
B) Oracle 
C) MongoDB 
D) React 
✅ Ans: D 

Q47. Which company developed Windows? 
A) Apple 
B) Google 
C) Microsoft 
D) IBM 
✅ Ans: C 

Q48. Full form of USB: 
A) Universal Serial Bus 
B) Uniform System Bus 
C) Universal System Backup 
D) United Serial Bus 
✅ Ans: A 

Q49. Which technology is used in mobile apps? 
A) Bluetooth 
B) NFC 
C) Internet 
D) All of the above 
✅ Ans: D 

Q50. Which one is an example of hardware? 
A) Windows 
B) MS Word 
C) Keyboard 
D) Google Chrome 
✅ Ans: C 
"""

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("Connected to database")

        # Get Category ID for 'General Awareness/Technical/Computer Basics'
        cursor.execute("SELECT id FROM categories WHERE name = 'General Awareness/Technical/Computer Basics'")
        result = cursor.fetchone()
        
        if not result:
            print("Category 'General Awareness/Technical/Computer Basics' not found! Creating it...")
            cursor.execute("INSERT INTO categories (name) VALUES ('General Awareness/Technical/Computer Basics')")
            conn.commit()
            category_id = cursor.lastrowid
        else:
            category_id = result[0]
            
        print(f"Using Category ID: {category_id}")

        questions = []
        current_q = {}
        lines = raw_data.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match Question (e.g., Q1. ...)
            q_match = re.match(r'^Q\d+\.\s*(.+)', line)
            if q_match:
                # Save previous question
                if current_q:
                    questions.append(current_q)
                
                current_q = {
                    'question_text': q_match.group(1).strip(),
                    'options': {},
                    'correct': '',
                    'category_id': category_id
                }
                continue
            
            # Match Options (e.g., A) ...)
            opt_match = re.match(r'^([A-D])\)\s*(.+)', line)
            if opt_match and current_q:
                opt = opt_match.group(1)
                text = opt_match.group(2).strip()
                current_q['options'][opt] = text
                continue
                
            # Match Answer (e.g., ✅ Ans: C)
            ans_match = re.search(r'✅ Ans:\s*([A-D])', line)
            if ans_match and current_q:
                current_q['correct'] = ans_match.group(1)
                continue
        
        # Add the last question
        if current_q:
            questions.append(current_q)
            
        print(f"Parsed {len(questions)} questions.")
        
        # Insert into database
        count = 0
        for q in questions:
            # Validate complete question
            if not q.get('question_text') or not q.get('correct') or len(q.get('options', {})) != 4:
                print(f"Skipping incomplete question: {q.get('question_text')[:30]}...")
                continue
                
            sql = """INSERT INTO questions 
                     (category_id, question_text, option_a, option_b, option_c, option_d, correct_option)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            
            val = (
                q['category_id'],
                q['question_text'],
                q['options'].get('A'),
                q['options'].get('B'),
                q['options'].get('C'),
                q['options'].get('D'),
                q['correct']
            )
            
            try:
                cursor.execute(sql, val)
                count += 1
            except mysql.connector.Error as err:
                print(f"Error inserting question: {err}")
                
        conn.commit()
        print(f"Successfully inserted {count} questions into the database.")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
