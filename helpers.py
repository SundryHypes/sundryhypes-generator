# Copyright Severin Josef Burg 2023
# Any unauthorised usage forbidden


def remove_thats_right(text):
    text = text.replace("That's right. ", '')

    return text


def remove_awkward_comma_names(text):
    punctuation_signs = ['.', ',', ';', ':', '!', '?', ' ']
    hosts = ['Marc', 'Giulia']
    for host in hosts:
        for sign in punctuation_signs:
            text = text.replace(f', {host}{sign}', sign)

    return text
