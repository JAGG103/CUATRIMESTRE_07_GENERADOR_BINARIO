from MODULES.ANALYZER.Analyzer import Analyzer
from MODULES.MUTATOR.Mutator import Mutator
from MODULES.CLASSIFICATOR.Classificator import Classificator
from MODULES.GENERATOR.Generator import Generator
import streamlit as st
import re
import json
import pandas as pd
import io
import copy

def play_sound(urlfile:str):
    st.write(f"""
        <audio id="sound" src="{urlfile}" autoplay></audio>
        <script>
            var audio = document.getElementById("sound");
            audio.play();
        </script>
    """, unsafe_allow_html=True)

def save_tcs_as_json(tcs:dict, name:str):
    file = json.dumps(tcs)
    st.download_button(
        label="Dowload test cases .json",
        data=file,
        file_name= f"{name}.json",
        mime="application/json"
    )

def save_tcs_as_csv(tcs:list, name:str):
    names = ["Inputs", "outputs"]
    tcs.insert(0, names)
    df = pd.DataFrame(tcs[1:], columns=tcs[0])
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    st.download_button(
        label="Download test cases .csv",
        data=csv_buffer.getvalue(),
        file_name=f'{name}.csv',
        mime='text/csv'
    )


def init_generation(specification:str, parameters:dict):

    with st.spinner("Analizing specification"):
        a = Analyzer(specification)
    with st.spinner("Mutating specifications"):
        m = Mutator(a.prels, copy.deepcopy(a.testconditions), copy.deepcopy(a.defconditions))
    with st.spinner("Classificating predicates"):
        c = Classificator(copy.deepcopy(m.testconditions), copy.deepcopy(m.defconditions))
    with st.spinner("Generating test cases"):
        g = Generator(parameters, a.inport, a.inaux, a.outport, a.outaux, a.init, c.testconditions, c.defconditions)
    
    tcsList = []
    tcsDict = dict()
    for i in range(len(g.testcase_suite)):
        tcsDict[f"Test:{i}"] = {"input":g.testcase_suite[i][1][0], "output":g.testcase_suite[i][1][1]}
        tcsList.append([g.testcase_suite[i][0][0], g.testcase_suite[i][0][1] ])
    notpossible = dict()
    for i in range(len(g.notsatinds)):
        notpossible[f"not possible:{i}"] = {"test Condition":m.testconditions[g.notsatinds[i]] ,
                                            "definition Condition":m.defconditions[g.notsatinds[i]]} 

    st.success("Complete")
    audio_file = 'https://www.soundjay.com/buttons/sounds/button-8.mp3'
    play_sound(audio_file)
    return (tcsDict, tcsList, notpossible, a.name)

# --------------------- main------------------------------

sb = st.sidebar.radio("Select a way upload spec.", options={"upload .txt file", "write specification"})

st.title("Automatic Test Case Generator Using Genetic Algorithm")

with st.form("Parameters"):
    colProb, colPop, colGen = st.columns(3)
    prob = colProb.text_input("Probability", value=0.03)
    pop =colPop.text_input("Population", value=100)
    gen = colGen.text_input("Generations", value=200)
    colDist, colTries = st.columns(2)
    dist = colDist.text_input("Distance of domain", value=100)
    tries = colTries.text_input("Number of tries", value=5)
    buttonSub = st.form_submit_button("Submit")
    parameters = {'m_probability':float(prob),'n_population':int(pop), 'generations':int(gen), 'distance':int(dist), 'tries':int(tries)}

if(sb=="upload .txt file"):
    specObj = st.file_uploader("Upload the specificaction in SOFL (.txt)", type="txt")
    if specObj is not None:
        specification = specObj.read().decode("utf-8")
        st.text_area("Specification in SOFL", specification, height=400)
        buttonus = st.button("Generate Test Cases")
        if(buttonus):
            pattern = "\\r"
            specification = re.sub(pattern, "", specification)
            out = init_generation(specification, parameters) # Tool inicialization
            st.text("Test Cases")
            st.write(out[0])
            st.text("Insatisfied Conditions")
            st.write(out[2])
            save_tcs_as_json(out[0], out[3])
            save_tcs_as_csv(out[1], out[3])

else:
    specification = st.text_area("Write specification", value="")
    if( len(specification)>0 ):
        buttonws = st.button("Generate Test Cases")
        if(buttonws):
            out = init_generation(specification, parameters) # Tool inicialization
            st.text("Test Cases")
            st.write(out[0])
            st.text("Insatisfied Conditions")
            st.write(out[2])
            save_tcs_as_json(out[0], out[3])
            save_tcs_as_csv(out[1], out[3])


