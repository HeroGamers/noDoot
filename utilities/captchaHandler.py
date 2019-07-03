import os, random, string
from captcha.image import ImageCaptcha

def generateCaptcha():
    # First we generate a random string to use // Changed to only use lowercase letters, as by user requests
    chars = string.ascii_lowercase + string.digits
    text = ''.join(random.choice(chars) for x in range(5))

    # And generate the captcha
    captchaimage = ImageCaptcha()

    image = captchaimage.generate_image(text)

    # Now to add some noise
    captchaimage.create_noise_curve(image, image.getcolors())
    captchaimage.create_noise_dots(image, image.getcolors())

    # Now to write the file
    filenumber = 0
    while True:
        if os.path.exists("./img/captcha_" + str(filenumber) + ".png"):
            filenumber += 1
        else:
            break
    imagefile = "./img/captcha_" + str(filenumber) + ".png"
    captchaimage.write(text, imagefile)

    return imagefile, text