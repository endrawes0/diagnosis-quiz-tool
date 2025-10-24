#!/usr/bin/env python3
"""
Script to generate realistic clinical cases to replace generic template cases.
This creates cases with specific symptoms rather than "symptoms consistent with X".
"""

import json
import random
from typing import Dict, List, Any

# Templates for generating realistic cases by diagnosis
CASE_TEMPLATES = {
    "erectile disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to a urology clinic with a {duration}-month history of difficulty achieving and maintaining erections sufficient for satisfactory sexual intercourse. He reports that erections occur occasionally but are not firm enough for penetration. The problem has caused significant distress and he now avoids initiating intimacy due to fear of failure. He denies morning erections and has noticed decreased libido. He has hypertension treated with a thiazide diuretic and drinks alcohol socially. He feels embarrassed and questions his masculinity.",
            "A {age}-year-old {gender} is referred by his primary care physician for evaluation of erectile dysfunction. For the past {duration} months, he has been unable to achieve erections despite sexual stimulation. He describes erections that start but then fade quickly. This has led to avoidance of sexual activity and strain on his relationship. He reports feeling anxious and depressed about the situation. He has diabetes mellitus and takes metformin. He denies tobacco use but admits to occasional recreational drug use.",
            "A {age}-year-old {gender} comes to the clinic concerned about his sexual performance. He reports that over the past {duration} months, erections have become unreliable and often insufficient for intercourse. He describes partial erections that don't last long enough. This has caused him significant anxiety and he has started avoiding intimate situations. He has a history of coronary artery disease and takes multiple cardiac medications. He reports feeling stressed at work and has trouble sleeping.",
        ],
        "ages": {"male": (25, 70), "female": (25, 70)},
        "durations": [2, 3, 5, 6, 8, 10, 12]
    },

    "posttraumatic stress disorder": {
        "presentations": [
            "A {age}-year-old {gender} Iraq War veteran presents to the VA clinic with complaints of poor sleep and irritability. He served as a combat soldier and was involved in several firefights where he witnessed the deaths of fellow soldiers. Since returning home {duration} months ago, he has had frequent nightmares of combat scenes and wakes up in a sweat. He experiences flashbacks triggered by loud noises that remind him of gunfire, during which he feels as if he is back in that situation. He avoids crowded places and any news about the war, saying it makes him feel on edge. His wife notes that he is often jumpy at sudden sounds and has become emotionally distant. He drinks alcohol nightly to 'calm his nerves.'",
            "A {age}-year-old {gender} presents to the mental health clinic reporting intrusive memories and nightmares since a serious car accident {duration} months ago. She was the driver in a collision that killed her passenger and left her with multiple injuries. Since then, she has recurrent flashbacks of the accident, especially when driving or hearing sirens. She avoids highways and gets extremely anxious when other cars approach too closely. She has trouble sleeping due to nightmares and feels constantly on guard. Her concentration at work has suffered and she has become socially withdrawn. She reports feeling emotionally numb and has lost interest in previously enjoyed activities.",
            "A {age}-year-old {gender} comes to the clinic after experiencing a home invasion {duration} months ago. Since the incident, she has been unable to sleep in her bedroom and has installed multiple locks and security cameras throughout her home. She has recurrent nightmares about the intruder and experiences panic attacks when she hears unfamiliar noises at night. She avoids going out alone after dark and has quit her job because the commute made her too anxious. Her family reports that she startles easily and has become irritable and emotionally distant. She reports feeling guilty for surviving when others in similar situations have not.",
        ],
        "ages": {"male": (20, 60), "female": (18, 65)},
        "durations": [2, 3, 4, 5, 6, 9, 10, 11]
    },

    "major neurocognitive disorder due to alzheimer's disease": {
        "presentations": [
            "A {age}-year-old {gender} is brought to the neurology clinic by her daughter due to progressive memory problems. Over the last {duration} months, she has had increasing difficulty remembering recent events and often repeats the same questions. She recently got lost while driving to a familiar grocery store. At home, she sometimes forgets to turn off the stove or leave the water running. Her family notes changes in her personality; she has become more apathetic and occasionally irritable, whereas she was previously very lively and engaged. There have been no hallucinations or delusional beliefs. Her medical history is unremarkable aside from well-controlled hypertension. An MRI showed generalized cortical atrophy consistent with Alzheimer's disease.",
            "A {age}-year-old {gender} presents with his wife who reports that he has become increasingly forgetful over the past {duration} months. He forgets appointments, misplaces objects, and has trouble following conversations. He has gotten lost while walking in their neighborhood on several occasions. He becomes frustrated and angry when he can't remember things, and has withdrawn from social activities. He has trouble with basic calculations and has stopped managing their finances. There is no history of stroke or head trauma. His wife notes that he sometimes accuses her of hiding his belongings when he can't find them. Neuropsychological testing shows deficits in memory and executive functioning.",
            "A {age}-year-old {gender} is evaluated after her family noticed she has been having trouble with daily activities. For the past {duration} months, she has forgotten how to use the microwave and has left food burning on the stove. She repeats stories and questions multiple times during conversations. She has become lost while shopping at her usual grocery store. Her family reports that she seems more apathetic and has lost interest in hobbies she previously enjoyed. She occasionally becomes suspicious that people are stealing from her. There are no focal neurological signs, and her general medical examination is normal. Brain imaging shows diffuse cortical atrophy.",
        ],
        "ages": {"male": (60, 85), "female": (55, 90)},
        "durations": [3, 4, 7, 8, 9, 10, 11]
    },

    "enuresis": {
        "presentations": [
            "A {age}-year-old {gender} is brought to the pediatrician by his parents due to bedwetting. He has been wetting the bed about 4 nights per week for the past {duration} months. He had achieved nighttime continence by age 4 and stayed dry for several years, but the bedwetting resumed after the family moved to a new home. There are no daytime accidents, and no medical issues have been identified on physical exam and urinalysis. The boy says he feels embarrassed and avoids sleepovers. The parents have tried limiting fluids in the evening and waking him at night, with little success. There is no history of constipation or urinary tract infections.",
            "A {age}-year-old {gender} presents with his mother who reports that he continues to wet the bed despite being {age} years old. The bedwetting has been occurring 3-5 times per week for the past {duration} months. He was dry at night for about 2 years but the problem returned after his parents' divorce. He denies daytime wetting and has normal urinary function during the day. Physical examination and urinalysis are normal. He reports feeling ashamed and has become reluctant to have friends sleep over. His mother notes that he seems more anxious and has trouble concentrating at school. There is no family history of bedwetting.",
            "A {age}-year-old {gender} is evaluated for persistent bedwetting. Despite being toilet trained since age 2, she has been wetting the bed 2-3 times per week for the past {duration} months. The problem started after her grandmother died and she began having nightmares. She has normal daytime bladder control and no urinary symptoms. Physical exam and urine studies are unremarkable. She reports feeling embarrassed and has stopped inviting friends for playdates. Her parents note that she seems more clingy and has trouble separating at bedtime. There is no history of abuse or significant stressors beyond the recent loss.",
        ],
        "ages": {"male": (7, 15), "female": (7, 15)},
        "durations": [3, 4, 6, 7, 9, 11]
    },

    "conduct disorder": {
        "presentations": [
            "A {age}-year-old {gender} is brought to juvenile court for evaluation after multiple arrests for theft and vandalism. Over the past {duration} months, he has been involved in physical fights at school and was expelled for assaulting a classmate. He has also been caught shoplifting and was recently accused of breaking into a neighbor's garage. His parents report long-standing behavioral issues, including chronic lying and skipping school. They describe him as having little remorse when he hurts others or gets into trouble. There is a history of cruelty to animals as a child, and he appears to get a 'thrill' from intimidating younger children. No evidence of an underlying medical condition is present, and substance use has been denied.",
            "A {age}-year-old {gender} presents to the child psychiatry clinic after being suspended from school for aggressive behavior. For the past {duration} months, she has been involved in multiple physical altercations with peers and has destroyed school property on several occasions. She has been caught stealing money from classmates and lying about it when confronted. Her teachers report that she shows no remorse and often blames others for her actions. At home, she has been defiant toward her parents, staying out past curfew and ignoring household rules. She has a history of setting fires and being cruel to pets. There are no signs of intellectual disability or other neurodevelopmental disorders.",
            "A {age}-year-old {gender} is referred for evaluation after being arrested for burglary. He has a history of conduct problems dating back to early childhood, but they have escalated over the past {duration} months. He has been truant from school, has run away from home multiple times, and has been involved in fights and property destruction. He shows no empathy for victims and often rationalizes his behavior. His parents report that he has always been oppositional and has never responded well to discipline. He began using marijuana at age 12 and currently uses it daily. There is a family history of antisocial behavior and substance abuse.",
        ],
        "ages": {"male": (12, 17), "female": (12, 17)},
        "durations": [2, 3, 5, 6, 7, 9, 10, 12]
    },

    "major depressive disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to the clinic with a two-month history of worsening mood. He reports feeling sad nearly every day and has lost interest in his usual hobbies, including playing guitar and going out with friends. His energy is low and he often stays in bed for hours. His appetite has markedly decreased, and he has unintentionally lost 15 pounds in the last month. He struggles to concentrate at work and has been making mistakes that could cost him his job. He admits to feelings of worthlessness and guilt, blaming himself for being 'weak' and burdening his family. He denies any history of manic or hypomanic episodes. He has fleeting thoughts that life isn't worth living but denies any specific plan or intent to harm himself.",
            "A {age}-year-old {gender} comes to the mental health clinic reporting persistent low mood and lack of motivation. For the past {duration} months, she has felt depressed most days, with little interest in activities she previously enjoyed. She has trouble getting out of bed in the morning and often calls in sick to work. Her sleep is disrupted with early morning awakening, and she has lost 10 pounds due to decreased appetite. She feels guilty about not being able to care for her children properly and worries that she's a bad mother. Concentration is poor and she has trouble remembering things. She denies suicidal ideation but admits to feeling that the world would be better without her.",
            "A {age}-year-old {gender} is brought in by his wife who is concerned about his worsening depression. Over the past {duration} months, he has become increasingly withdrawn and irritable. He has lost interest in his job and often sits alone in the garage for hours. His appetite has decreased significantly, leading to a 20-pound weight loss. He has trouble sleeping, waking up at 4 AM and being unable to fall back asleep. He reports feeling worthless and has been having thoughts of death, though he denies active suicidal planning. He has a family history of depression and previously had a similar episode 5 years ago that responded to antidepressants.",
        ],
        "ages": {"male": (25, 65), "female": (20, 70)},
        "durations": [2, 3, 4, 5, 7, 8, 12]
    },

    "autism spectrum disorder": {
        "presentations": [
            "A {age}-year-old {gender} is brought to the developmental pediatrics clinic by his parents due to concerns about his social development and repetitive behaviors. Since early childhood, he has had difficulty making friends and prefers to play alone. He has intense interests in specific topics like trains or dinosaurs, talking about them for hours and becoming upset if interrupted. He has routines that must be followed exactly, becoming distressed when they change. He has trouble understanding social cues, often taking things literally and missing sarcasm. He avoids eye contact and has delayed language development, though he now speaks in complex sentences about his interests. He has sensory sensitivities, covering his ears at loud noises and refusing certain textures of food. His parents report that he had developmental delays and received early intervention services.",
            "A {age}-year-old {gender} presents to the adult psychiatry clinic after losing his job due to social difficulties. He reports lifelong challenges with social interactions, having few friends and struggling to understand social norms. He has intense interests in computer programming and can spend hours coding without breaks. He follows strict routines and becomes anxious when they are disrupted. He has trouble reading facial expressions and body language, often misunderstanding jokes or social cues. He prefers solitary activities and has difficulty initiating or maintaining conversations. He has sensory sensitivities to bright lights and loud sounds. He was diagnosed with Asperger's syndrome as a child but lost his diagnosis when transitioning to adult services. He reports feeling isolated and depressed about his social difficulties.",
            "A {age}-year-old {gender} is evaluated after her school reported concerns about her social communication and restricted interests. She has few friends and prefers solitary play, often lining up toys or organizing objects rather than imaginative play. She has intense interests in particular topics like animals or numbers, collecting extensive information about them. She has trouble with reciprocal conversation, often monologuing about her interests without noticing if others are disinterested. She takes language literally and misses implied meanings. She has sensory sensitivities, becoming overwhelmed in noisy environments and seeking out specific textures. Her parents note that she had early developmental concerns and received speech therapy. She has some restricted food preferences and insists on wearing the same clothes.",
        ],
        "ages": {"male": (5, 45), "female": (5, 40)},
        "durations": [12, 24, 36, 48, 60]  # Lifelong condition, duration represents age of presentation
    },

    "gender dysphoria": {
        "presentations": [
            "A {age}-year-old {gender} presents to the gender clinic expressing distress about his assigned gender at birth. Since childhood, he has felt that he was meant to be male, preferring boys' activities and clothing. He binds his chest to flatten his breasts and wears masculine clothing. He uses a male name and pronouns when possible. He experiences significant anxiety and depression related to his gender incongruence, avoiding social situations where he might be misgendered. He reports suicidal ideation when thinking about living the rest of his life in the 'wrong body.' He has researched hormone therapy and gender-affirming surgery. His family is supportive but he worries about societal rejection. He has no history of psychosis or other mental health conditions.",
            "A {age}-year-old {gender} comes to the clinic after years of hiding her gender identity. She has always felt female despite being assigned male at birth. She cross-dresses when possible and has been taking estrogen from online sources. She experiences severe dysphoria when seeing her male genitalia and avoids mirrors. She has social anxiety due to fear of rejection and has isolated herself from family. She reports chronic depression and has attempted suicide twice. She works as a software developer but feels distracted by gender thoughts. She has been in therapy for several years and is ready to pursue medical transition. She has no other psychiatric diagnoses.",
            "A {age}-year-old {gender} is referred by his therapist for evaluation of gender dysphoria. He reports feeling male since age 4, preferring masculine play and rejecting feminine clothing. He has been living as male socially for the past year, using a chosen name and pronouns. He experiences distress when referred to as female and has been bullied at school. He has symptoms of anxiety and depression, with poor concentration and social withdrawal. He has researched puberty blockers and hopes to start them soon. His parents are divided in their support, with his mother accepting but his father rejecting his identity. He has no history of gender exploration or other identity issues.",
        ],
        "ages": {"male": (13, 35), "female": (14, 40)},
        "durations": [2, 3, 5, 7, 10, 15, 20]
    },

    "anorexia nervosa": {
        "presentations": [
            "A {age}-year-old {gender} is brought to the eating disorders clinic by her mother who is concerned about her daughter's weight loss and restrictive eating. Over the past {duration} months, she has lost 25 pounds, dropping from a healthy BMI to dangerously low levels. She restricts her intake to minimal amounts, often skipping meals entirely and eating only small portions of 'safe' foods like lettuce and carrots. She weighs herself multiple times daily and becomes distressed if the scale shows any increase. She exercises excessively, running 5-6 miles daily despite feeling weak. She reports feeling fat even though she is visibly underweight. She has amenorrhea and complains of feeling cold all the time. Her thoughts are preoccupied with food, calories, and body image. She denies that she has a problem and becomes defensive when her eating is questioned.",
            "A {age}-year-old {gender} is admitted to the inpatient eating disorders unit after her weight dropped dangerously low. She has been restricting her intake for {duration} months, eating only 300-500 calories daily. She has lost 40 pounds and her BMI is 13.5. She has intense fear of gaining weight and views her thinness as an achievement. She has rituals around food preparation and avoids eating with others. She has stopped menstruating and has low heart rate and blood pressure. She reports feeling 'fat' and worthless when she eats. Her family reports that she has become irritable and withdrawn. She has been hospitalized before for similar issues but relapsed after discharge. She expresses desire to recover but feels terrified of weight gain.",
            "A {age}-year-old {gender} presents to the emergency room after collapsing at school. Her BMI is critically low at 14. She has lost 30 pounds over the past {duration} months through severe caloric restriction and excessive exercise. She eats very little, often just drinking black coffee and eating a few crackers daily. She has rituals around food preparation and avoids eating with others. She has lanugo hair growth and complains of constipation and cold intolerance. She reports feeling satisfied when hungry and views her thinness as an achievement. She has withdrawn from friends and family, spending most time alone. Her school performance has declined due to fatigue and poor concentration. She admits to occasional binge eating followed by purging, though restriction is her primary method. She feels out of control when eating and uses restriction to regain control.",
        ],
        "ages": {"male": (14, 25), "female": (13, 30)},
        "durations": [3, 4, 6, 8, 10, 12, 18]
    },

    "narcolepsy": {
        "presentations": [
            "A {age}-year-old {gender} presents to the sleep clinic complaining of excessive daytime sleepiness and sudden sleep attacks. For the past {duration} months, he has been falling asleep unexpectedly during meetings, while driving, and even during conversations. He describes cataplexy episodes where his knees buckle suddenly when he laughs or gets excited, though he doesn't lose consciousness. He has vivid hallucinations when falling asleep and upon awakening. His sleep at night is fragmented with frequent awakenings. He feels refreshed after naps but the sleepiness returns quickly. He has gained weight despite eating normally. He reports feeling embarrassed about falling asleep at work and has been reprimanded for poor performance. He denies using recreational drugs or alcohol. His symptoms started gradually and have worsened over time.",
            "A {age}-year-old {gender} comes to the neurology clinic after multiple 'fainting' episodes. She describes sudden loss of muscle tone triggered by strong emotions like laughter or surprise, causing her to collapse but remain conscious. For the past {duration} months, she has had overwhelming sleepiness, falling asleep while eating, watching TV, or talking on the phone. She has hypnagogic hallucinations of seeing people in her room when falling asleep. Her nighttime sleep is disrupted with frequent awakenings. She has gained 20 pounds without changing her diet. She has been diagnosed with 'seizures' in the past but EEG was normal. She reports feeling depressed about her condition and has stopped socializing. She has trouble concentrating and her work performance has suffered.",
            "A {age}-year-old {gender} is evaluated for excessive sleepiness that has interfered with his daily functioning. Over the past {duration} months, he has had irresistible sleep attacks, falling asleep while driving (with near accidents), during classes, and at social events. He experiences cataplexy with partial muscle weakness in his face and arms when excited. He has sleep paralysis upon awakening, feeling unable to move for several minutes. His sleep is fragmented at night with multiple awakenings. He has automatic behaviors, continuing activities while asleep. He reports feeling refreshed after short naps but sleepy again soon after. He has been diagnosed with depression and ADHD in the past, but stimulants made his sleepiness worse. He feels frustrated and has become socially isolated.",
        ],
        "ages": {"male": (15, 45), "female": (12, 50)},
        "durations": [6, 8, 10, 12, 15, 18, 24]
    },

    "obsessive-compulsive disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to the anxiety clinic reporting intrusive thoughts and compulsive behaviors that interfere with his daily life. For the past {duration} months, he has had persistent fears of contamination, washing his hands dozens of times daily until they bleed. He avoids touching doorknobs or shaking hands. He has checking compulsions, returning home multiple times to ensure the stove is off and doors are locked. These rituals take hours daily and cause significant distress. He recognizes that his fears are excessive but cannot stop. He has become socially isolated, avoiding restaurants and public transportation. His work performance has declined due to time spent on rituals. He reports feeling anxious and depressed. He has tried to ignore the thoughts but they return stronger. No history of tic disorders or other psychiatric conditions.",
            "A {age}-year-old {gender} comes to the clinic after her husband insisted she seek help. She has been struggling with OCD symptoms for {duration} months. She has intrusive thoughts that she might harm her children, leading to avoidance of being alone with them. She checks that appliances are off repeatedly and has elaborate cleaning rituals. She spends 4-5 hours daily on these compulsions. She feels compelled to count objects and arrange things symmetrically. She avoids situations that trigger obsessions, like public restrooms. Her rituals interfere with work and relationships. She reports feeling exhausted and has symptoms of depression. She has tried exposure therapy in the past with some success but relapsed. No substance use or other mental health issues.",
            "A {age}-year-old {gender} is evaluated for debilitating anxiety symptoms. He has had obsessions about symmetry and order for {duration} months, spending hours arranging objects perfectly. He has contamination fears, showering multiple times daily and changing clothes frequently. He has mental compulsions like counting or repeating phrases to neutralize bad thoughts. He avoids situations that trigger obsessions, like public restrooms. His rituals interfere with work and relationships. He feels ashamed of his symptoms and has not told anyone. He reports feeling depressed and has suicidal thoughts. He has tried SSRIs prescribed by his PCP with partial relief. He has a family history of anxiety disorders. He wants help to control his impulses.",
        ],
        "ages": {"male": (18, 50), "female": (16, 55)},
        "durations": [6, 8, 10, 12, 15, 18, 24]
    },

    "opioid use disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to the addiction clinic after being arrested for prescription fraud. He started using oxycodone for back pain 2 years ago and developed dependence. For the past {duration} months, he has been taking higher doses and crushing pills to snort them. He experiences withdrawal symptoms like nausea, sweating, and anxiety when trying to stop. He has lost his job and strained relationships with family. He has been to detox twice but relapsed quickly. He reports feeling ashamed but continues using. He has tried methadone but didn't like the program. He has chronic pain from a work injury. He denies other substance use but admits to drinking occasionally. He expresses desire for help but fears withdrawal. He has symptoms of depression and anxiety.",
            "A {age}-year-old {gender} is brought to the ER by her boyfriend after overdosing on heroin. She has been using opioids for {duration} months, starting with prescription painkillers after dental surgery. She progressed to heroin when prescriptions ran out. She injects daily and has developed abscesses at injection sites. She has lost 30 pounds and has poor hygiene. She has been arrested for possession and lost custody of her children. She experiences severe withdrawal with vomiting, diarrhea, and muscle aches. She has tried buprenorphine but stopped taking it. She reports feeling hopeless and has suicidal ideation. She has hepatitis C from needle sharing. She wants to stop but feels trapped. No other substance use disorders.",
            "A {age}-year-old {gender} comes to the clinic seeking medication-assisted treatment. He has been addicted to opioids for {duration} months, starting with prescription pain medication after surgery. He now uses heroin daily and has developed tolerance, needing increasing amounts. He has withdrawal symptoms when attempting abstinence. He has lost his job and home, living with friends. He has been in rehab twice but relapsed. He has chronic pain and uses opioids to manage it. He reports feeling depressed and anxious. He has tried counseling but found it unhelpful. He is motivated for treatment and wants to start buprenorphine. He has no other substance use but smokes cigarettes. He has a family history of addiction.",
        ],
        "ages": {"male": (20, 50), "female": (18, 45)},
        "durations": [6, 8, 10, 12, 15, 18, 24]
    },

    "conversion disorder (functional neurological symptom disorder)": {
        "presentations": [
            "A {age}-year-old {gender} presents to the neurology clinic with sudden onset of weakness in her right arm and leg. The symptoms began {duration} weeks ago after an argument with her husband. She has normal sensation and reflexes, and MRI of the brain and spinal cord are normal. She reports feeling stressed about marital problems and her mother's recent death. She has a history of similar episodes in the past that resolved spontaneously. She appears anxious during examination and has a inconsistent pattern of weakness. She reports feeling frustrated that doctors can't find a cause. She has symptoms of depression and uses the weakness to avoid responsibilities. She denies secondary gain but her husband notes she receives more attention when symptomatic. No history of trauma or abuse.",
            "A {age}-year-old {gender} is evaluated for episodes of seizures that don't respond to anticonvulsants. For the past {duration} months, she has had frequent 'seizures' characterized by shaking and loss of awareness, but EEG shows no epileptiform activity. The episodes occur in front of others and she recovers quickly. She has a history of childhood abuse and current marital stress. She reports feeling numb in her extremities and has difficulty walking at times. Physical examination shows normal strength and coordination. She has been diagnosed with epilepsy and tried multiple medications. She reports feeling misunderstood by doctors. She has symptoms of anxiety and depression. She acknowledges stress triggers her symptoms but feels they are involuntary.",
            "A {age}-year-old {gender} comes to the clinic with unexplained blindness in both eyes. The vision loss occurred suddenly {duration} weeks ago during a stressful work evaluation. Ophthalmologic examination shows normal eye structures and no visual pathway abnormalities. She has inconsistent visual field testing. She reports feeling overwhelmed at work and has a history of panic attacks. She has been seen by multiple specialists with normal findings. She uses a white cane and has stopped working. She reports feeling depressed and anxious. She has a history of somatization and multiple unexplained physical symptoms. She denies malingering but acknowledges stress worsens her symptoms. Family history of anxiety disorders.",
        ],
        "ages": {"male": (25, 55), "female": (20, 60)},
        "durations": [1, 2, 3, 4, 6, 8, 12]
    },

    "borderline personality disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to the emergency room after overdosing on pills following a breakup. She has a history of unstable relationships, intense fear of abandonment, and impulsive behaviors. For the past {duration} months, she has had frequent mood swings, feeling euphoric one moment and suicidal the next. She has chronic feelings of emptiness and identity disturbance. She has cut herself multiple times when feeling overwhelmed. Her relationships are intense but short-lived, often ending in conflict. She has been fired from several jobs due to emotional outbursts. She reports feeling chronically misunderstood and has been in therapy multiple times. She has symptoms of depression and anxiety. She acknowledges her behaviors cause problems but feels unable to control them.",
            "A {age}-year-old {gender} is admitted to the psychiatric unit after a suicide attempt. She has a long history of unstable interpersonal relationships and self-harm. Over the past {duration} months, she has been intensely involved with a new partner but became enraged when he didn't respond to texts immediately, accusing him of abandoning her. She has chronic feelings of emptiness and has tried multiple identities. She has dissociative episodes when stressed. She has been in multiple abusive relationships. She reports feeling numb emotionally most of the time. Her family reports she becomes a different person during episodes. She has symptoms of depression, anxiety, and PTSD. She has tried multiple therapies and medications. She feels hopeless about ever feeling stable.",
            "A {age}-year-old {gender} comes to the clinic after being arrested for assault during an argument. She has a pattern of intense, unstable relationships and fear of abandonment. For the past {duration} months, she has been cycling through periods of idealizing then devaluing her therapist. She has chronic suicidal ideation and has made multiple attempts. She reports feeling empty and has engaged in risky behaviors like unprotected sex and substance use. She has trouble controlling anger and has destroyed property during rages. She has been hospitalized several times. She acknowledges her diagnosis but feels treatments haven't helped. She has co-occurring depression and PTSD from childhood trauma.",
        ],
        "ages": {"male": (18, 40), "female": (16, 45)},
        "durations": [6, 8, 10, 12, 15, 18, 24]
    },

    "exhibitionistic disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to the sexual disorders clinic after being arrested for indecent exposure. He reports a long-standing urge to expose himself in public, starting in adolescence. For the past {duration} months, he has been exposing himself to women in parks and shopping centers, feeling sexually aroused by their reactions. He masturbates to fantasies of exposure. He feels distressed by his urges but continues the behavior. He has been arrested twice and fears losing his job if caught again. He reports feeling ashamed and has tried to stop but relapses under stress. He has a stable relationship but his partner is unaware. He denies other paraphilias. He has symptoms of anxiety and depression. He wants help to control his impulses.",
            "A {age}-year-old {gender} is referred by his attorney after a conviction for public indecency. He has been exposing his genitals to strangers for {duration} months, feeling intense sexual excitement from the risk and surprise. He has done this in various public places and has been caught multiple times. He reports the behavior started after a divorce and increased during stressful periods. He feels guilty afterward but the urges return. He has tried therapy in the past but stopped. He reports feeling depressed about his actions. He has a girlfriend who suspects something but he denies it. He has no other criminal history. He expresses motivation for treatment to avoid jail time.",
            "A {age}-year-old {gender} comes to the clinic after his wife discovered his secret behavior. He has been exposing himself to women for {duration} months, often in his car or at work. He feels sexually gratified by their shock and fear. He reports feeling compelled to act on urges despite knowing it's wrong. He has been close to getting caught several times. He feels distressed by his behavior and wants to stop. He has symptoms of anxiety and low self-esteem. He has tried masturbating to non-exposure fantasies but it doesn't satisfy. He has a history of childhood sexual abuse. He is committed to treatment.",
        ],
        "ages": {"male": (25, 60), "female": (20, 55)},
        "durations": [6, 8, 10, 12, 15, 18, 24]
    },

    "dissociative identity disorder": {
        "presentations": [
            "A {age}-year-old {gender} presents to the trauma clinic with memory gaps and different 'parts' of herself. She reports having distinct personality states that take control at different times. For the past {duration} months, she has experienced blackouts and lost time, discovering things she doesn't remember doing. She has child-like alters who come out during stress, and angry alters who protect her. She has dissociative amnesia for traumatic events from childhood. She reports severe childhood abuse by multiple perpetrators. She has been diagnosed with depression, anxiety, and PTSD. She experiences depersonalization and derealization. She has tried multiple therapies and hospitalizations. She feels confused and frightened by her symptoms. She has self-harm behaviors and suicidal ideation.",
            "A {age}-year-old {gender} is brought by her husband who reports dramatic personality changes. She has been diagnosed with DID after {duration} months of evaluation. She has multiple alters including a protector, a child, and a persecutor. She experiences switching between alters, with amnesia between states. She has flashbacks of severe childhood trauma. She reports feeling detached from her body and emotions. She has chronic depression and anxiety. She has been in therapy for years with limited progress. Her husband describes different mannerisms and voices during switches. She has PTSD symptoms and uses dissociation to cope. She feels fragmented and wants to integrate. She has co-occurring eating disorder. She reports feeling unreal and has identity confusion.",
            "A {age}-year-old {gender} comes to the clinic after being triggered by a news story. She has DID with {duration} months of documented switches. She has alters with different ages, genders, and functions. She experiences time loss and discovers injuries she doesn't remember getting. She has severe childhood trauma history. She reports feeling like different people live inside her. She has depression, anxiety, and self-harm. She has been in specialized trauma therapy. She switches during sessions. She feels fragmented and wants to integrate. She has co-occurring eating disorder. She reports feeling unreal and has identity confusion.",
        ],
        "ages": {"male": (20, 50), "female": (18, 55)},
        "durations": [12, 18, 24, 30, 36, 48, 60]
    },

    "bipolar i disorder": {
        "presentations": [
            "A {age}-year-old {gender} is brought to the psychiatric emergency room by his family during a manic episode. For the past {duration} weeks, he has been extremely energetic, sleeping only 2-3 hours per night but feeling rested. He has been spending money recklessly, buying expensive items he can't afford. He has grandiose ideas about his business abilities and has quit his job to start a new venture. He talks rapidly and jumps between topics. He has increased sexual activity and made inappropriate advances. He denies any problems and becomes irritable when questioned. His family reports similar episodes in the past that lasted weeks and were followed by deep depressions. He has a history of depression treated with antidepressants. He has been drinking more alcohol during this episode.",
            "A {age}-year-old {gender} presents to the clinic in a mixed episode with both manic and depressive symptoms. She has been irritable and agitated for {duration} weeks, with racing thoughts and pressured speech. She feels worthless and hopeless while also having grandiose ideas. She has decreased need for sleep but feels exhausted. She has been overspending and engaging in risky behaviors. She reports feeling both euphoric and despairing simultaneously. She has suicidal ideation but also feels invincible. She has a history of manic episodes requiring hospitalization. She stopped her mood stabilizer 3 months ago. She has symptoms of anxiety and psychosis during episodes. Her family reports she becomes a different person during episodes.",
            "A {age}-year-old {gender} is evaluated after a manic episode led to job loss and divorce. He has been stable for years on lithium but had a breakthrough episode {duration} weeks ago. He became hyperactive, working 20-hour days on creative projects. He had inflated self-esteem and made unrealistic plans. He spent thousands on impulsive purchases. He had increased libido and multiple sexual partners. He became paranoid and believed people were plotting against him. He didn't sleep for days but felt energetic. He crashed into a severe depression afterward. He has had multiple hospitalizations. He reports feeling terrified of another episode. He has good insight when euthymic. He wants to adjust his medication regimen.",
        ],
        "ages": {"male": (20, 50), "female": (18, 45)},
        "durations": [1, 2, 3, 4, 6, 8, 12]
    }
}

def generate_realistic_case(case_id: str, diagnosis: str, age: int, gender: str, duration: int) -> Dict[str, Any]:
    """Generate a realistic case based on diagnosis template."""

    if diagnosis not in CASE_TEMPLATES:
        # Fallback for diagnoses without templates
        return {
            "case_id": case_id,
            "category": "Unknown",
            "age_group": "adult" if age >= 18 else "child",
            "diagnosis": diagnosis,
            "narrative": f"A {age}-year-old {gender} presents with symptoms of {diagnosis.lower()}.",
            "MSE": "Mental status examination reveals normal appearance and behavior.",
            "complexity": "basic",
            "difficulty_tier": "beginner",
            "xp_value": 50
        }

    template = CASE_TEMPLATES[diagnosis]
    presentation = random.choice(template["presentations"])

    # Format the presentation with actual values
    narrative = presentation.format(
        age=age,
        gender=gender,
        duration=duration
    )

    # Generate MSE based on diagnosis
    mse_templates = {
        "Erectile Disorder": "The patient appears well-groomed and cooperative. He makes good eye contact but seems embarrassed when discussing sexual issues. Speech is normal in rate and tone. Mood is described as anxious and depressed, affect congruent. Thought processes are logical. No evidence of hallucinations or delusions. He is oriented and cognitively intact. Insight is good regarding the problem, judgment appropriate.",
        "Posttraumatic Stress Disorder": "The patient appears anxious and avoids eye contact initially. He is cooperative but seems hypervigilant, frequently scanning the environment. Speech is hesitant at first but becomes more fluent. Mood is anxious and depressed, affect restricted. Thought processes show some circumstantiality when discussing trauma. No hallucinations but endorses intrusive memories. Fully oriented. Insight is fair, judgment intact though avoidance behaviors noted.",
        "Major Neurocognitive Disorder due to Alzheimer's Disease": "The patient is neatly dressed but appears confused at times. She maintains eye contact but seems apathetic. Speech is slow with word-finding difficulties. Mood is neutral, affect blunted. Thought processes are concrete with impaired abstraction. No hallucinations or delusions currently. Disoriented to time, memory deficits evident. Insight is limited, judgment impaired.",
        "Enuresis": "The child appears his stated age, cooperative but embarrassed. Makes good eye contact. Speech is age-appropriate. Mood is anxious, affect congruent. Thought processes are logical for age. No psychotic symptoms. Fully oriented. Good insight into the problem, judgment intact.",
        "Conduct Disorder": "The adolescent appears defiant and avoids eye contact. He is minimally cooperative. Speech is monosyllabic. Mood irritable, affect labile. Thought processes show poor judgment. No hallucinations or delusions. Fully oriented. Poor insight, judgment impaired.",
        "Major Depressive Disorder": "The patient appears tired and disheveled. Makes poor eye contact. Speech is slowed and monotonous. Mood depressed, affect constricted. Thought processes show pessimism and self-deprecation. No hallucinations or delusions. Fully oriented but concentration impaired. Fair insight, judgment intact.",
        "Autism Spectrum Disorder": "The patient appears his stated age but makes intermittent eye contact. He is cooperative but seems uncomfortable with social interaction. Speech is formal and pedantic, with advanced vocabulary but atypical prosody. Mood is neutral, affect restricted. Thought processes are logical but concrete, with intense focus on specific interests. No hallucinations or delusions. Fully oriented. Insight is limited regarding social difficulties, judgment intact in structured situations.",
        "Gender Dysphoria": "The patient appears anxious and maintains variable eye contact. She is cooperative but seems guarded. Speech is hesitant when discussing gender issues. Mood is depressed and anxious, affect congruent. Thought processes are logical with preoccupation on gender identity. No hallucinations or delusions. Fully oriented. Good insight into distress, judgment appropriate.",
        "Anorexia Nervosa": "The patient appears emaciated but well-groomed. She makes good eye contact but seems anxious. Speech is normal in rate but focused on food/weight. Mood is anxious and depressed, affect restricted. Thought processes show distorted body image and food preoccupation. No hallucinations but endorses overvalued ideas about weight. Fully oriented. Poor insight into illness severity, judgment impaired regarding eating.",
        "Narcolepsy": "The patient appears tired and has dark circles under eyes. He makes good eye contact but seems drowsy. Speech is normal but he occasionally pauses as if falling asleep. Mood is neutral to depressed, affect congruent. Thought processes are logical. No hallucinations or delusions. Fully oriented. Good insight, judgment intact though impaired by sleepiness.",
        "Obsessive-Compulsive Disorder": "The patient appears anxious and makes good eye contact. He is cooperative but seems distressed. Speech is normal but hesitant. Mood is anxious, affect congruent. Thought processes show obsessive rumination and compulsive planning. No hallucinations or delusions. Fully oriented. Good insight into symptoms being excessive, judgment intact.",
        "Opioid Use Disorder": "The patient appears disheveled and has track marks on arms. He makes intermittent eye contact and seems anxious. Speech is normal but he appears distracted. Mood is depressed and anxious, affect congruent. Thought processes are logical but preoccupied with drug use. No hallucinations or delusions. Fully oriented. Fair insight, judgment impaired by addiction.",
        "Conversion Disorder (Functional Neurological Symptom Disorder)": "The patient appears anxious and makes good eye contact. She is cooperative but seems frustrated. Speech is normal. Mood is anxious and depressed, affect congruent. Thought processes are logical. No hallucinations or delusions. Fully oriented. Variable insight, judgment intact.",
        "Borderline Personality Disorder": "The patient appears anxious and makes intense eye contact. She is cooperative initially but becomes emotional. Speech is pressured at times. Mood is labile, affect congruent. Thought processes are logical but show splitting. No hallucinations or delusions. Fully oriented. Poor insight into interpersonal patterns, judgment impaired in relationships.",
        "Exhibitionistic Disorder": "The patient appears anxious and avoids eye contact initially. He is cooperative but seems ashamed. Speech is hesitant when discussing sexual issues. Mood is depressed and anxious, affect congruent. Thought processes are logical. No hallucinations or delusions. Fully oriented. Good insight into problem, judgment appropriate.",
        "Dissociative Identity Disorder": "The patient appears anxious and makes variable eye contact. She switches between different presentation styles during interview. Speech varies in tone and content. Mood is labile, affect congruent. Thought processes show dissociation. No hallucinations but reports alters. Fully oriented. Variable insight, judgment intact.",
        "Bipolar I Disorder": "The patient appears energetic and makes good eye contact. He is cooperative but seems grandiose. Speech is rapid and pressured. Mood is euphoric, affect expansive. Thought processes are logical but show flight of ideas. No hallucinations or delusions currently. Fully oriented. Poor insight during episodes, judgment impaired."
    }

    mse = mse_templates.get(diagnosis, "Mental status examination reveals normal appearance, cooperative behavior, normal speech, neutral mood with congruent affect, coherent thought processes, no hallucinations or delusions, intact cognition, fair insight, and intact judgment.")

    # Determine category and complexity
    category_map = {
        "erectile disorder": "Sexual Dysfunctions",
        "posttraumatic stress disorder": "Trauma- and Stressor-Related Disorders",
        "major neurocognitive disorder due to alzheimer's disease": "Neurocognitive Disorders",
        "enuresis": "Elimination Disorders",
        "conduct disorder": "Disruptive, Impulse-Control, and Conduct Disorders",
        "major depressive disorder": "Depressive Disorders",
        "autism spectrum disorder": "Neurodevelopmental Disorders",
        "gender dysphoria": "Gender Dysphoria",
        "anorexia nervosa": "Feeding and Eating Disorders",
        "narcolepsy": "Sleep-Wake Disorders",
        "obsessive-compulsive disorder": "Obsessive-Compulsive and Related Disorders",
        "opioid use disorder": "Substance-Related and Addictive Disorders",
        "conversion disorder (functional neurological symptom disorder)": "Somatic Symptom and Related Disorders",
        "borderline personality disorder": "Personality Disorders",
        "exhibitionistic disorder": "Paraphilic Disorders",
        "dissociative identity disorder": "Dissociative Disorders",
        "bipolar i disorder": "Bipolar and Related Disorders"
    }

    category = category_map.get(diagnosis, "Unknown")
    complexity = "moderate"
    difficulty_tier = "intermediate"
    xp_value = 100

    return {
        "case_id": case_id,
        "category": category,
        "age_group": "adult" if age >= 18 else ("adolescent" if age >= 13 else "child"),
        "diagnosis": diagnosis,
        "narrative": narrative,
        "MSE": mse,
        "complexity": complexity,
        "difficulty_tier": difficulty_tier,
        "xp_value": xp_value,
        "clinical_specifiers": [],
        "unlock_requirements": {"min_level": 1},
        "prevalence_weight": 1.0,
        "symptom_variants": [],
        "differential_combinations": []
    }

def main():
    """Main function to replace generic cases with realistic ones."""

    # Load existing cases
    with open('data/cases.json', 'r') as f:
        cases = json.load(f)

    updated_count = 0

    for case in cases:
        narrative = case.get('narrative', '')

        # Check if this is a generic case with either pattern
        diagnosis = None
        if 'symptoms consistent with' in narrative and 'various psychiatric symptoms' in narrative:
            # Extract diagnosis from the "symptoms consistent with" pattern
            diagnosis_start = narrative.find('symptoms consistent with ') + len('symptoms consistent with ')
            diagnosis_end = narrative.find('.', diagnosis_start)
            diagnosis = narrative[diagnosis_start:diagnosis_end].strip()
        elif 'presents with symptoms of' in narrative:
            # Extract diagnosis from the "presents with symptoms of" pattern
            diagnosis_start = narrative.find('presents with symptoms of ') + len('presents with symptoms of ')
            diagnosis_end = narrative.find('.', diagnosis_start)
            if diagnosis_end == -1:  # If no period found, take to end of string
                diagnosis = narrative[diagnosis_start:].strip()
            else:
                diagnosis = narrative[diagnosis_start:diagnosis_end].strip()

        if diagnosis:
            # Extract age and gender
            age_match = narrative.split('-year-old ')
            if len(age_match) > 1:
                age_str = age_match[0].split()[-1]
                try:
                    age = int(age_str)
                except ValueError:
                    age = 30  # default

                gender_part = age_match[1].split()[0]
                gender = gender_part if gender_part in ['male', 'female'] else 'male'

                # Generate new realistic case
                new_case = generate_realistic_case(
                    case['case_id'],
                    diagnosis,
                    age,
                    gender,
                    6  # default duration
                )

                # Update the case
                case.update(new_case)
                updated_count += 1
                print(f"Updated case {case['case_id']}: {diagnosis}")
            else:
                print(f"Could not parse age/gender for case {case['case_id']}: {narrative[:100]}...")

    # Save updated cases
    with open('data/cases.json', 'w') as f:
        json.dump(cases, f, indent=2)

    print(f"\nUpdated {updated_count} generic cases with realistic clinical presentations.")

if __name__ == "__main__":
    main()