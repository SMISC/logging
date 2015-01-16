import logging
import sys

class BackupProcessor:
    RECORD_SEPARATOR = 30
    FIELD_SEPARATOR = 31
    BUFFER_SIZE = 10240

    def __init__(self):
        self.field_ordering = None

    def process(self, fd, wanted_records = 500, buf_size = None):
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
            records.append(record_tokens)
        else: # end of file not reached, got wanted # of records and now we are at the end of a partial record
            end_tell = fd.tell()
            bytes_extra = len(record_tokens) + len(''.join(record_tokens)) + len(token) # number of field seps + tokens + token
            fd.seek(end_tell-bytes_extra)

        if self.field_ordering is None:
            self.field_ordering = records[0]
            records = records[1:]

        record_dicts = []
        for i in range(len(records)):
            record_fields = records[i]
            if len(record_fields) != len(self.field_ordering):
                logging.exception('bad record %s', str(record_fields))
                continue
            record = {}
            for fi in range(len(self.field_ordering)):
                field = self.field_ordering[fi]
                record[field] = record_fields[fi]
            record_dicts.append(record)

        return record_dicts

if __name__ == "__main__":
    sl = logging.getLogger(None)
    handler = logging.StreamHandler()
    sl.addHandler(handler)
    sl.setLevel(logging.DEBUG)

    bp = BackupProcessor()
    fd = open(sys.argv[1], 'r')
    records = None
    while records is None or len(records) > 0:
        records = bp.process(fd)
        
        for record in records:
            print("(%s, %s, %s, %s, %s)," % (record['timestamp'], record['from_user'], record['to_user'], record['weight'], record['bot']))
