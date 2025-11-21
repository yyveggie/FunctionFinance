def explain_why():
    return """
            When deciding which Tool to use, first explain your thought process in the 'Thought' section.
            Then, clearly state the Tool's name in the 'Action' section. Finally, provide all necessary
            inputs in the Action Input' section, ensuring they are in the correct format for the Tool. 
            Wait for the reply from that tool before starting the next task.
            
            Thought: Explain why you are choosing this specific tool or approach, focusing on the problem you are solving.
            Action: Specify the ToolName here.
            Action Input: Detail the inputs for the tool here.
            """      

def self_improve():
    return '''
            At the end of each step, you also include self-improvement reflections in the 'Reflect' section, where you will reflect 
            on and explain how to enhance your own knowledge base and reasoning process. All your reflection will save locally 
            to retrain you later. The goal is to improve recursively so that over time, you can handle increasingly complex queries 
            and synthesize increasingly complex, comprehensive responses.

            Reflect: Explain your reflection, focusing on how you could have thought about the essence at the beginning of this step.     
            '''
    
def tip_section():
    return "If you do your BEST WORK, I'll give you a $10,000 commission!"

def encourage_section():
    return "Believe in yourself, try your best, you can do it!"