from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import tensorflow as tf

slim = tf.contrib.slim
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nets'))
import nets

