"""Import dependencies"""
import os
import warnings
from datetime import datetime
import whisper
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

#Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=ImportWarning)


# Load environment variables
load_dotenv("metting_summarization.env")

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file. Please add it before running")

# Audio Transcriber Compoments(whisper)

class AudioTranscriber:

    """Used to transcribe audio to text"""

    def __init__(self,model_size="base"):
        #load whisper model
        print(f"loading whisper model {model_size} ...")
        self.model=whisper.load_model(model_size,device="cpu")
        print("whisper model load successfully")

   
    def transcribe(self,audio_path,language="en"):
        """Initial transcibtion"""
        print(f"loading transcribe {audio_path} ...")
        result=self.model.transcribe(
            audio_path,
            language=language,
            verbose=False
        )
        print("transcription complete")
        return {
            "text":result['text'],
            "language":result["language"],
            "segments":result["segments"]

        }

class MeetingSummarization:
    """meeting summarization using crewai and gemini"""
    def __init__(self,api_key=None):
        self.llm=LLM(
            model="gemini-2.5-flash",
            api_key=API_KEY or os.getenv(API_KEY),
            temperature=0.3
        )

        self.agent = Agent(
            role="Meeting Minutes Specialist",
            goal=(
                "Create comprehensive, well-structured meeting summaries "
                "covering key points, decisions, and action items"
            ),
            backstory=("""You are an expert at analyzi  ng meeting transcripts and \n
                    extracting the most important information.\n
                    You organize information clearly with proper heading and bullet points.\n
                    You identify key decisions, action items ,and important discussions."""),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def summarize(self, transcript):
        """Create task for the agent"""
        task = Task(
            description=f"""
                Analyze the following meeting 
                transcript and create a comprehensive summary.

                Transcript:
                {transcript}

                Your summary must include:
                1. **Meeting Overview**: Brief description of the meeting purpose
                2. **Key Discussion points**: Main topics discussed (bullet points)
                3. **Decision Made**: Important decisions and conclusions.
                4. **Action Items**: Tasks assigned with responsible persons (if mentioned)
                5. **Open Questions**: unresolved issues or questions raised

                Format the output with clear headings and bullet points for easy reading.
            """,
            expected_output=(
                "A well-structured meeting summary with all "
                "key information organized under clear headings"
            ),
            agent=self.agent
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        result= crew.kickoff()
        
        return result

#Context Aware Meeting Summarization Pipeline for documentation

class MeetingSummarizationPipeLine:
    """Context-Aware Meeting Summarization Pipeline"""
    def __init__(self,whisper_model_size="base",api_key=None):
        self.transcriber=AudioTranscriber(model_size=whisper_model_size)
        self.summarizer=MeetingSummarization(api_key=api_key)
    
    def run(self,audio_path,language="en",save_output=True):
        """Process the Audio file"""
        print("\n" + "="*60)
        print("meeting summarization pipeline started")
        print("="*60 + "\n")

        #step 1 Transcribe audio
        print("Transcribing audio ...")
        transcription_output=self.transcriber.transcribe(audio_path,language)
        transcript=transcription_output["text"]
        print(f"transcript Length{len(transcript)} character")

        # step 2 Context-Aware Summarization of  transcript
        print("start summarization")
        summary=self.summarizer.summarize(transcript)

        #Save transcript and Context-Aware summarization
        if save_output:
            today_date_and_time=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            transcript_file=f"meeting_transcript{today_date_and_time}.txt"

            with open(transcript_file,"w",encoding="utf-8") as file:
                file.write(transcript)
            #print(f'Transcript saved {transcript_file}')

            summary_file=f"meeting_summary_{today_date_and_time}.txt"
            with open(summary_file,'w',encoding="utf-8") as file:
                file.write(str(summary))
            #print(f"summary file saved{summary_file}")

            print("\n" + "="*60)
            print("Context Aware Meeting Summarization is Complete")
            print("="*60 + "\n")

            return {
                "transcript":transcript_file,
                "summary":summary_file,
                "metadata":{
                    "language":transcription_output['language'],
                    "timestamp": datetime.now().isoformat()
                }
            }
            

if __name__=="__main__":
    #Audio Path
    audio_file= "/Users/mihirverma/Meeting_Summarizer_Agent/amicorpus/ES2008a/audio/ES2008a.Mix-Headset.wav"
    
    pipepline=MeetingSummarizationPipeLine(
                whisper_model_size="base",
                api_key="API_KEY"
    )
    report=pipepline.run(audio_file)

    print("="*60)
    print("Transcript")
    print("="*60)
    print(report["transcript"])
    print("\n" + "="*60)
    print('REPORT')
    print("="*60)
    print(report["summary"])





        

 