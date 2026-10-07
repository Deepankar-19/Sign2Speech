"""One-off: regenerate ISL_INCLUDE_NEW.onnx from the .keras model.
Run on a machine WITH AVX (not the server):
  pip install "tensorflow>=2.16,<2.21" tf2onnx onnx
  python convert_to_onnx.py
"""
import subprocess, sys
import tensorflow as tf
m = tf.keras.models.load_model("ISL_INCLUDE_NEW.keras", compile=False)
m.export("_saved_model", format="tf_saved_model")
subprocess.check_call([sys.executable, "-m", "tf2onnx.convert", "--saved-model",
                       "_saved_model", "--output", "ISL_INCLUDE_NEW.onnx", "--opset", "17"])
