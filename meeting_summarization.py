import os
import warnings
from datetime import datetime
import whisper
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

load_dotenv("metting_summarization.env")

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file.")

class AudioTranscriber:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size, device="cpu")
   
    def transcribe(self, audio_path, language="en"):
        print(f"Transcribing {audio_path}...")
        result = self.model.transcribe(audio_path, language=language, verbose=False)
        return {
            "text": result['text'],
            "language": result["language"],
            "segments": result["segments"]
        }

class MeetingSummarization:
    def __init__(self, api_key=None):
        self.llm = LLM(
            model="gemini-2.5-flash",
            api_key=API_KEY or api_key,
            temperature=0.3
        )
        self.agent = Agent(
            role="Meeting Minutes Specialist",
            goal="Create comprehensive, well-structured meeting summaries covering key points, decisions, and action items",
            backstory="You are an expert at analyzing meeting transcripts and extracting the most important information. You organize information clearly with proper headings and bullet points.",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def summarize(self, transcript):
        task = Task(
            description=f"""
                Analyze the following meeting transcript and create a comprehensive summary.
                Transcript:
                {transcript}

                Your summary must include:
                1. **Meeting Overview**: Brief description of the meeting purpose
                2. **Key Discussion points**: Main topics discussed
                3. **Decisions Made**: Important decisions and conclusions
                4. **Action Items**: Tasks assigned
                5. **Open Questions**: Unresolved issues

                Format with clear headings and bullet points.
            """,
            expected_output="A well-structured meeting summary.",
            agent=self.agent
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        return crew.kickoff()

class MeetingSummarizationPipeLine:
    def __init__(self, whisper_model_size="base", api_key=None):
        self.transcriber = AudioTranscriber(model_size=whisper_model_size)
        self.summarizer = MeetingSummarization(api_key=api_key)
    
    def run(self, audio_path, language="en", save_output=True):
        print("\n" + "="*60 + "\nMeeting summarization pipeline started\n" + "="*60)

        transcription_output = self.transcriber.transcribe(audio_path, language)
        transcript = transcription_output["text"]
        
        summary = self.summarizer.summarize(transcript)

        if save_output:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            transcript_file = f"meeting_transcript_{timestamp}.txt"
            summary_file = f"meeting_summary_{timestamp}.txt"

            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript)

            with open(summary_file, 'w', encoding="utf-8") as f:
                f.write(str(summary))

            print("\n" + "="*60 + "\nPipeline Complete\n" + "="*60)

            return {
                "transcript": transcript_file,
                "summary": summary_file,
                "metadata": {
                    "language": transcription_output['language'],
                    "timestamp": datetime.now().isoformat()
                }
            }