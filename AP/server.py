from flask import Flask, send_file
from torchvision.utils import save_image
from torch.autograd.variable import Variable
import torch
import os
from torch import nn

z_dim = 100

class Generator(nn.Module):
    def __init__(self, z_dim):
        super(Generator, self).__init__()
        self.gen = nn.Sequential(
            nn.Linear(z_dim, 256),
            nn.LeakyReLU(),
            nn.Linear(256, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 1024),
            nn.LeakyReLU(),
            nn.Linear(1024, 3*64*64),  # para gerar imagens 64x64 com 3 canais (RGB)
            nn.Tanh()
        )

    def forward(self, input):
        return self.gen(input)

gen = Generator(z_dim)
#torch.save(gen.state_dict(),"gerador.pth")
gen.load_state_dict(torch.load("Geradores/gerador2515.pth",map_location=torch.device("cpu")))
gen.eval()



# as classes do gerador e discriminador, bem como a função test_generator, deveriam estar aqui

app = Flask(__name__)

@app.route('/obter-imagem', methods=['GET'])
def obter_imagem():
    num_samples = 1
    z = Variable(torch.randn(num_samples, z_dim))
    gen.eval()
    with torch.no_grad():
        gen_imgs = gen(z).view(-1, 3, 64, 64)

    # salva a imagem gerada no disco
    save_image(gen_imgs, "gan_image.png", normalize=True)

    return send_file('gan_image.png', mimetype='image/png')

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Expose-Headers', '*')
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
