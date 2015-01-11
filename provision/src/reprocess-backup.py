import logging
import sys

class BackupProcessor:
    RECORD_SEPARATOR = 30
    FIELD_SEPARATOR = 31
    BUFFER_SIZE = 10240

    def __init__(self):
        pass

    def process(self, fd, wanted_records = 1, buf_size = None):
        '''Try to read a whole number of records from the fd, returning a list of tokens and resetting the position to the beginning of th next record'''
        if buf_size is None:
            buf_size = self.BUFFER_SIZE
        buf = None
        records = []
        record_tokens = []
        token = ""

        while buf is None or (buf != "" and len(records) < wanted_records):
            buf = fd.read(buf_size)
            for i in range(0, len(buf)):
                char = buf[i]

                if ord(char) == self.FIELD_SEPARATOR:
                    record_tokens.append(token)
                    token = ""
                    continue
                elif ord(char) == self.RECORD_SEPARATOR:
                    records.append(record_tokens)
                    record_tokens = []
                    continue
                else:
                    token += char

        if buf == "": # end of file
            records.push(record_tokens)
        else: # end of file not reached, got wanted # of records and now we are at the end of a partial record
            end_tell = fd.tell()
            bytes_extra = len(chr(self.FIELD_SEPARATOR).join(record_tokens)) + len(token)
            fd.seek(end_tell-bytes_extra)

        return records

if __name__ == "__main__":
    sl = logging.getLogger(None)
    handler = logging.StreamHandler()
    sl.addHandler(handler)
    sl.setLevel(logging.DEBUG)

    bp = BackupProcessor()
    fd = open(sys.argv[1], 'r')
    for i in range(int(sys.argv[3])):
        records = bp.process(fd, int(sys.argv[2]), int(sys.argv[4]))
        handler.flush()
        print(str(records))
