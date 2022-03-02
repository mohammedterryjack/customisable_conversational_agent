# Task Policy

## Features Explained in 11 Examples
---
### 1. Adding a Task (e.g. 'Jump')

To add a task, you simply need to declare the task name (its good practise to name your task with a word that the user would utter to request such a task - e.g. "jump", "run", "chat", "talk", etc). 

```yaml
Tasks:
    Jump:
```

Since there is nothing declared under this task, the system will just respond one of the default replies if this task is activated 

e.g.
- User: *I want you to jump* ... System: *I don't know how to Jump*
- User: *I said jump!* ... System: *I can't Jump!*

---
### 2. Using Custom Replies 

If you wish to add your own custom replies, simply define them under the action like so:

```yaml 
Tasks:
    Greet:
        Action:
            Say:
                - Hi
                - Hello
```
e.g.
- User: *Hi* ... System: *Hello*
- User: *Hi* ... System: *Hi*

---

### 3. Using Actions

```yaml
Tasks:
    RadioOn:
        Action:
            Say:
                - Sure
            Do:
                - PlayRadio()
```
e.g. 
- User: *Play the radio* ... System: *Sure [radio turns on]*

---
### 4. Replying with an action's output 

```yaml
Tasks:
    Time:
        Action:
            Say:
                - The time now is __TimeNow__
            Do:
                - TimeNow()
    Chat:
        Action:
            Say:
                - Sure, __MyGenerator__
            Do:
                - MyGenerator()
```
e.g.
- User: *What's the time?* ...System: *the time now is 3pm*
- User: *Lets chat* ... System: *Sure, Do you know what happened to me today at school?*

---
### 5. Using Slots
You can use any slot in your reply (just be sure to use the actual slot name precisely)

```yaml
Tasks:
    Greet:
        Action:
            Say:
                - Hello {name}
                - Hi {name}. Nice to meet you!
        Memory:
            name:
Slots:
    name:
```
e.g.
- User: *Hi I'm Mary* ... System: *Hi Mary. Nice to meet you!*

---
### 6. Setting Default Slot Values
e.g. 
- User: *Hi* ... System: *Hi Buddy. Nice to meet you!*

```yaml
Tasks:
    Greet:
        Action:
            Say:
                - Hello {name}
                - Hi {name}. Nice to meet you!
        Memory:
            name:
                Default: Buddy
Slots:
    name:
```
---
### 7. Prompting the User for Missing Slot Values

```yaml
Tasks:
    Greet:
        Action:
            Say:
                - Hello {name}
                - Hi {name}. Nice to meet you!
        Memory:
            name:
                Prompt: Who are you?
Slots:
    name:
```
e.g.
- User: *Hi*  ... System: *Who are you?*
- User: *I'm Mary* ... System: *Hi Mary. Nice to meet you!*

---
### 8. Querying Slot Values

You can also query a slot that has been set in a conversation by asking about the slot directly.  

e.g.
- User: *Hi I'm Mary* ... System: *Hi Mary. Nice to meet you!*
- User: *What's my name?* ... System: *Mary*

Or if it doesnt have a value set it will respond with "I dont know the SLOT"

e.g.
- User: *What's the time of departure?* ... System: *I don't know the time of departure*

If you want to override the default replies given, you can override the default behaviour by specifying a task in the yaml file called "QuerySlot..." (followed by the name of the slot )

```yaml
Tasks:
    QuerySlotName:
        Action:
            Say:
                - Your name is {name}
        Memory:
            name:
                Prompt: I don't know your name
Slots:
    name:
```
e.g.
- User: *Hi I'm Mary* ... System: *Hi Mary. Nice to meet you!*
- User: *What's my name?* ... System: *Your name is Mary*

---

### 9. Using Slots in Actions
The prompts will trigger whenever a slot has no value and is being used in a template. This behaviour can be done for as many slots as you like.  You may also like to add slots as inputs to non-verbal actions too 

```yaml
Tasks:
    BookTicket:
        Action:
            Say:
                - Your ticket to {destination} for {arrival_time} by {transportation} is being booked
            Do:
                - book_ticket(
                    destination={destination},
                    departure_time={departure_time},
                    arrival_time={arrival_time},
                    transportation={transportation}
                )
        Memory:
            destination:
                Prompt: Where to?
            departure_time:
                Default: now
            arrival_time:
                Prompt: When do you want to arrive?
            transportation:
                Prompt: Which type of transport will you be using?
Slots:
    destination:
    departure_time:
    arrival_time:
    transportation:
```
e.g.
- User: *Book me a ticket to Manchester* ... System: *Which type of transport will you be using?*
- User: *Im going by bus* ...System: *When do you want to arrive?*
- User: *I want to arrive by 8pm* ...System: *Your ticket to Manchester for 8pm by bus is being booked*

---

### 10. Changing a Slot's Scope
Now if you use the same slot in different tasks, the value will automatically updates all instances of that slot across tasks (a Slot's scope is Global by default).  

```yaml
Tasks:
    Greet:
        Action:
            Say:
                - Hello {name}
                - Hi {name}. Nice to meet you!
        Memory:
            name:
                Prompt: Who are you?
    KnockKnockJoke:
        Action:
            Say:
                - {name} who?
        Memory:
            name:
                Prompt: Who's there?
    Laugh:
        Action:
            Say:
                - lol
                - haha
Slots:
    name:
```
e.g.
- User: *Knock Knock* ... System: *Who's there?*
- User: *R2* ... System: *R2 who?*
- User: *R2 D2* ... System: *lol*
- User: *Hi* ... System: *Hello R2*

This can lead to unwanted behaviour in some cases (as in the example above). So you can specify a slot to have a Local scope within a certain task (so that the value updated within that task will not propogate to all other tasks)

```yaml
Tasks:
    Greet:
        Action:
            Say:
                - Hello {name}
                - Hi {name}. Nice to meet you!
        Memory:
            name:
                Prompt: Who are you?
    KnockKnockJoke:
        Action:
            Say:
                - {name} who?
        Memory:
            name:
                Scope: Local
                Prompt: Who's there?
    Laugh:
        Action:
            Say:
                - lol
                - haha
Slots:
    name:
```

e.g.
- User: *Knock Knock* ... System: *Who's there?*
- User: *R2* ... System: *R2 who?*
- User: *R2 D2* ... System: *lol*
- User: *Hi* ... System: *Who are you?*
- User: *I'm Mary* ... System: *Hello Mary*
---

### 11. Custom Task Triggers

By default, each task is selected based on the decision of an inbuilt TaskClassifier.  However, you can customise this behaviour by specifying additional conditions which make use of the full range of features (e.g. `intent`, `topic`, `system_utterance`, `predicted_tasks`, `triggered_tasks`, any `slot`, etc)

```yaml
Tasks:
    Greet:
        Action:
            Say:
                - Hi {name}
                - Hello {name}
        TriggeredBy: ({intent}=='Greet' and {name}!='Mohammed')

    SecretGreet:
        Action:
            Say:
                - Greetings master. How may I be of service?
        TriggeredBy: ({intent}=='Greet' and {name}=='Mohammed')
Slots:
    name:
    task:
```
e.g. 
- User: *Hi its Mary* ... System: *Hi Mary*
- User: *Hi its Mohammed* ... System: *Greetings master. How may I be of service?*

You can even create conditions which make use of valid python syntax.  For example:
```yaml
Tasks:
    YesNo:
        TriggeredBy: '?' in {user_utterance} and not {user_utterance}.startswith('wh')
```

---

## Yaml File Structure

The full list of valid features you can add to the yaml file are shown below (note that many are optional and do not need to be specified manually)

```yaml
Tasks:
    MyTask:
        Action:
            Say:
                - an example utterance
                - an example utterance with {myslot}
                - an example utterance with the output of __cool_custom_logic__
            Do:
                - cool_custom_logic({myslot})
        Memory:
            myslot:
                Scope: Global
                Default: some default value for this slot
                Prompt: a question to ask the user for the value of this slot
        TriggeredBy: {myslot}=='someValue'
Slots:
    myslot:
```
