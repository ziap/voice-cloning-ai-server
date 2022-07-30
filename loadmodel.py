import sys
sys.path.append("model")

from pathlib import Path

from encoder.params_model import model_embedding_size as speaker_embedding_size
from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from utils.default_models import ensure_default_models
from vocoder import inference as vocoder

import numpy as np

model_path = Path("saved_models")

print("Preparing the encoder, the synthesizer and the vocoder...")
ensure_default_models(model_path)
encoder.load_model(Path("saved_models/default/encoder.pt"))
synthesizer = Synthesizer(Path("saved_models/default/synthesizer.pt"))
vocoder.load_model("saved_models/default/vocoder.pt")

# Export the models
preprocess_wav = encoder.preprocess_wav
embed_utterance = encoder.embed_utterance
synthesize_spectrograms = synthesizer.synthesize_spectrograms
sample_rate = synthesizer.sample_rate
hop_size = synthesizer.hparams.hop_size
infer_waveform = vocoder.infer_waveform

if __name__ == '__main__':
    print("\tTesting the encoder...")
    embed_utterance(np.zeros(encoder.sampling_rate))

    embed = np.random.rand(speaker_embedding_size)
    embed /= np.linalg.norm(embed)
    embeds = [embed, np.zeros(speaker_embedding_size)]
    texts = ["test 1", "test 2"]

    print("\tTesting the synthesizer... (loading the model will output a lot of text)")
    mels = synthesize_spectrograms(texts, embeds)

    mel = np.concatenate(mels, axis=1)

    print("\tTesting the vocoder...")
    infer_waveform(mel, target=200, overlap=50)

    print("All test passed! You can now synthesize speech.\n\n")
