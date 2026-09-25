import torch

from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
)


MODEL_ID = "AIHubSN/M-Kiriku-ASR"


class ASRService:

    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"[ASR] Chargement de {MODEL_ID}"
        )

        print(
            f"[ASR] Device : {self.device}"
        )

        self.processor = (
            WhisperProcessor.from_pretrained(
                MODEL_ID
            )
        )

        self.model = (
            WhisperForConditionalGeneration
            .from_pretrained(
                MODEL_ID,
            )
            .to(self.device)
        )

        self.model.eval()

        print("[ASR] Modèle chargé.")


    def transcribe(
        self,
        audio_path: str,
    ) -> str:

        import librosa

        audio, sample_rate = librosa.load(
            audio_path,
            sr=16000,
            mono=True,
        )

        inputs = self.processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt",
        )

        input_features = (
            inputs.input_features
            .to(self.device)
        )

        decoder_input_ids = torch.tensor(
            [
                [
                    self.processor.tokenizer.convert_tokens_to_ids(
                        "<|startoftranscript|>"
                    ),
                    self.processor.tokenizer.convert_tokens_to_ids(
                        "<|wo|>"
                    ),
                    self.processor.tokenizer.convert_tokens_to_ids(
                        "<|transcribe|>"
                    ),
                    self.processor.tokenizer.convert_tokens_to_ids(
                        "<|notimestamps|>"
                    ),
                ]
            ],
            device=self.device,
        )

        with torch.no_grad():

            predicted_ids = (
                self.model.generate(
                    input_features,
                    decoder_input_ids=decoder_input_ids,
                )
            )

        text = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True,
        )[0]

        return text.strip()
