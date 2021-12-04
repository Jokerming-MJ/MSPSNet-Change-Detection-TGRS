"""
test process by test datasets
Please cited:
Q. Guo, J. Zhang, S. Zhu, C. Zhong, and Y. Zhang. "Deep Multiscale Siamese Network with Parallel Convolutional Structure and Self-Attention for Change Detection" TGRS, 2021
"""
import warnings
import torch.utils.data
from tqdm import tqdm
from utils.parser import get_parser_with_args
from utils.Related import get_test_loaders
from sklearn.metrics import confusion_matrix

warnings.filterwarnings("ignore")

parser, metadata = get_parser_with_args()
opt = parser.parse_args()

dev = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
test_loader = get_test_loaders(opt)

"""load the weighted file and model"""
path = 'epoch_25.pt'
model = torch.load(path)

c_matrix = {'tn': 0, 'fp': 0, 'fn': 0, 'tp': 0}
model.eval()

with torch.no_grad():
    tbar = tqdm(test_loader)
    for batch_img1, batch_img2, labels in tbar:

        batch_img1 = batch_img1.float().to(dev)
        batch_img2 = batch_img2.float().to(dev)
        labels = labels.long().to(dev)

        cd_preds = model(batch_img1, batch_img2)
        cd_preds = cd_preds[-1]
        _, cd_preds = torch.max(cd_preds, 1)

        tn, fp, fn, tp = confusion_matrix(labels.data.cpu().numpy().flatten(),
                        cd_preds.data.cpu().numpy().flatten(),labels=[0,1]).ravel()

        c_matrix['tn'] += tn
        c_matrix['fp'] += fp
        c_matrix['fn'] += fn
        c_matrix['tp'] += tp

tn, fp, fn, tp = c_matrix['tn'], c_matrix['fp'], c_matrix['fn'], c_matrix['tp']
P = tp / (tp + fp)
R = tp / (tp + fn)
F1 = 2 * P * R / (R + P)

print('Precision: {}\nRecall: {}\nF1-Score: {}'.format(P, R, F1))
