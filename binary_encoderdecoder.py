from petlib.pack import encode, decode

class BinaryEncoderDecoder:
    def __init__(self, encoder_size = 64):
        self.size = encoder_size
        pass
    def encode_binary(self, l):
        string_conversion = "".join([str(x) for x in l])
        string_conversion = bytearray(string_conversion.encode())
        result = []
        while string_conversion:
            temporary_encoder = bytearray(string_conversion[:self.size])
            x = int(temporary_encoder, 2)
            petlib_encode = encode(x)
            string_conversion = string_conversion[self.size:]
            result.append(petlib_encode)
        return encode(result)

    def decode_binary(self, e, record_size):
        e = decode(e)
        result = ""
        for x in e:
            petlib_decode = decode(x)
            binary = "{0:b}".format(petlib_decode)
            print("PADDING LENGTH: ", (min(record_size, self.size) - len(binary)))
            pad = "0" * (record_size - len(binary))
            print(len(pad))
            result += pad + binary
        l = []
        for x in result:
            l.append(int(x))
        return l

if __name__ == '__main__':
    enc = BinaryEncoderDecoder()
    array = [1,0,0,1] * 1000000
    encoding =  enc.encode_binary(array)
    decoding = enc.decode_binary(encoding, 4000000)
    print(len(decoding), len(encoding))
    assert(decoding == array)
