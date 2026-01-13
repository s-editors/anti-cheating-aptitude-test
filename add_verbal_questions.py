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
Q1. Synonym of Happy 
A) Sad 
B) Angry 
C) Joyful 
D) Tired 
✅ Ans: C 

Q2. Antonym of Brave 
A) Bold 
B) Coward 
C) Strong 
D) Fearless 
✅ Ans: B 

Q3. Synonym of Begin 
A) End 
B) Stop 
C) Start 
D) Close 
✅ Ans: C 

Q4. Antonym of Early 
A) Fast 
B) Late 
C) Soon 
D) Now 
✅ Ans: B 

Q5. Synonym of Big 
A) Small 
B) Tiny 
C) Large 
D) Short 
✅ Ans: C 

Q6. Antonym of Hot 
A) Warm 
B) Cool 
C) Heat 
D) Fire 
✅ Ans: B 

Q7. Synonym of Fast 
A) Slow 
B) Quick 
C) Weak 
D) Late 
✅ Ans: B 

Q8. Antonym of Rich 
A) Wealthy 
B) Poor 
C) Strong 
D) Happy 
✅ Ans: B 

Q9. Synonym of Silent 
A) Loud 
B) Quiet 
C) Noisy 
D) Angry 
✅ Ans: B 

Q10. Antonym of Win 
A) Gain 
B) Beat 
C) Lose 
D) Achieve 
✅ Ans: C 

Q11. She is good ___ mathematics. 
A) in 
B) on 
C) at 
D) for 
✅ Ans: C 

Q12. He is afraid ___ dogs. 
A) from 
B) of 
C) with 
D) at 
✅ Ans: B 

Q13. I am fond ___ music. 
A) with 
B) of 
C) on 
D) at 
✅ Ans: B 

Q14. He depends ___ his parents. 
A) of 
B) on 
C) in 
D) at 
✅ Ans: B 

Q15. She insisted ___ paying the bill. 
A) at 
B) on 
C) in 
D) for 
✅ Ans: B 

Q16. He is married ___ a doctor. 
A) with 
B) to 
C) by 
D) at 
✅ Ans: B 

Q17. We are looking ___ the matter. 
A) into 
B) for 
C) at 
D) on 
✅ Ans: A 

Q18. The train arrived ___ time. 
A) in 
B) on 
C) at 
D) by 
✅ Ans: B 

Q19. He apologized ___ his mistake. 
A) for 
B) of 
C) at 
D) on 
✅ Ans: A 

Q20. She is capable ___ doing this work. 
A) to 
B) of 
C) in 
D) at 
✅ Ans: B 

Q21. Choose the correct sentence: 
A) He don’t like tea 
B) He doesn’t like tea 
C) He doesn’t likes tea 
D) He don’t likes tea 
✅ Ans: B 

Q22. She ___ completed her work. 
A) have 
B) has 
C) having 
D) had been 
✅ Ans: B 

Q23. I ___ to school every day. 
A) go 
B) goes 
C) going 
D) gone 
✅ Ans: A 

Q24. He ___ playing cricket now. 
A) is 
B) was 
C) were 
D) are 
✅ Ans: A 

Q25. They ___ finished the task. 
A) has 
B) have 
C) having 
D) is 
✅ Ans: B 

Q26. Choose correct passive voice: 
He wrote a letter. 
A) A letter is written by him 
B) A letter was written by him 
C) A letter has written by him 
D) A letter writes by him 
✅ Ans: B 

Q27. Identify the error: 
She do not like apples. 
A) She 
B) do 
C) like 
D) apples 
✅ Ans: B 

Q28. Choose correct tense: 
I ___ him yesterday. 
A) see 
B) saw 
C) seen 
D) seeing 
✅ Ans: B 

Q29. He is ___ honest man. 
A) a 
B) an 
C) the 
D) no article 
✅ Ans: B 

Q30. Choose the correct sentence: 
A) Each of the boys were present 
B) Each of the boys was present 
C) Each boys were present 
D) Each boys was present 
✅ Ans: B 

Q31. One who speaks many languages: 
A) Linguist 
B) Polyglot 
C) Orator 
D) Speaker 
✅ Ans: B 

Q32. One who loves books: 
A) Bibliophile 
B) Philanthropist 
C) Optimist 
D) Scholar 
✅ Ans: A 

Q33. A place where books are kept: 
A) Museum 
B) Library 
C) School 
D) Office 
✅ Ans: B 

Q34. One who looks at bright side: 
A) Pessimist 
B) Optimist 
C) Realist 
D) Egoist 
✅ Ans: B 

Q35. A handwriting difficult to read: 
A) Clear 
B) Legible 
C) Illegible 
D) Visible 
✅ Ans: C 

Q36. Fear of heights: 
A) Hydrophobia 
B) Claustrophobia 
C) Acrophobia 
D) Arachnophobia 
✅ Ans: C 

Q37. Study of animals: 
A) Botany 
B) Zoology 
C) Biology 
D) Ecology 
✅ Ans: B 

Q38. One who cannot read or write: 
A) Literate 
B) Scholar 
C) Illiterate 
D) Writer 
✅ Ans: C 

Q39. Killing of oneself: 
A) Homicide 
B) Suicide 
C) Regicide 
D) Patricide 
✅ Ans: B 

Q40. A life story written by oneself: 
A) Biography 
B) Autobiography 
C) Story 
D) Novel 
✅ Ans: B 

Q41. Choose correct plural of Child: 
A) Childs 
B) Children 
C) Childrens 
D) Childes 
✅ Ans: B 

Q42. Choose correct spelling: 
A) Enviroment 
B) Environment 
C) Environmant 
D) Enviornment 
✅ Ans: B 

Q43. Choose correct meaning of Abundant: 
A) Scarce 
B) Plenty 
C) Empty 
D) Poor 
✅ Ans: B 

Q44. Opposite of Success: 
A) Win 
B) Profit 
C) Failure 
D) Result 
✅ Ans: C 

Q45. Correct article: 
___ honest person 
A) A 
B) An 
C) The 
D) No article 
✅ Ans: B 

Q46. Choose correct sentence: 
A) He is senior than me 
B) He is senior to me 
C) He is senior from me 
D) He is senior of me 
✅ Ans: B 

Q47. Choose correct preposition: 
Interested ___ music 
A) on 
B) in 
C) at 
D) with 
✅ Ans: B 

Q48. Choose correct sentence: 
A) Neither of the answers are correct 
B) Neither of the answers is correct 
C) Neither answers is correct 
D) Neither answers are correct 
✅ Ans: B 

Q49. Correct form: 
He is good ___ singing 
A) in 
B) at 
C) on 
D) for 
✅ Ans: B 

Q50. Choose correct meaning of Brief: 
A) Long 
B) Short 
C) Wide 
D) Big 
✅ Ans: B 
"""

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("Connected to database")

        # Get Category ID for 'Verbal Ability'
        cursor.execute("SELECT id FROM categories WHERE name = 'Verbal Ability'")
        result = cursor.fetchone()
        
        if not result:
            print("Category 'Verbal Ability' not found! Creating it...")
            cursor.execute("INSERT INTO categories (name) VALUES ('Verbal Ability')")
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
