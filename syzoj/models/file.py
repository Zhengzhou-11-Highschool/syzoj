from syzoj import oj, db
import zipfile, os
import hashlib


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), index=True)
    md5 = db.Column(db.String(50), index=True)

    def __init__(self, file):
        self.file = file
        self.md5 = self.calc_md5(file)

    @staticmethod
    def calc_md5(file):
        file.seek(0)
        m = hashlib.md5()
        while True:
            data = file.read(8192)
            if not data:
                break
            m.update(data)

        md5 = m.hexdigest()
        return md5

    def save_file(self):
        self.file.seek(0)
        self.file.save(os.path.join(oj.config['UPLOAD_FOLDER'], self.md5))

    def get_file_path(self):
        return os.path.join(oj.config["UPLOAD_FOLDER"], self.md5)

    def save(self):
        db.session.add(self)
        db.session.commit()


class FileParser(object):
    @staticmethod
    def parse_as_testdata(file):
        filename = file.get_file_path()
        if not zipfile.is_zipfile(filename):
            return (False, "This file isn\'t zipfile")

        with zipfile.ZipFile(filename) as zip_file:
            file_list = zip_file.namelist()

            if "data_rule.txt" not in file_list:
                return (False, "Can\'t find data_rule.txt in testdata pack.")

            data_rule = zip_file.read("data_rule.txt")

            lines = data_rule.split('\n')
            for i in range(0, len(lines)):
                lines[i] = lines[i].replace('\r', '').replace('\n', '')

            if len(lines) < 3:
                return (False, "data_rule.txt should have 3 lines.")

            data_no = lines[0].split()
            input_name = lines[1]
            output_name = lines[2]

            ret = []

            for i in data_no:
                i = int(i)
                input_file = input_name.replace('#', str(i))
                output_file = output_name.replace('#', str(i))
                if input_file not in file_list:
                    return (False, "Can\'t find %s file." % input_file)
                if output_file not in file_list:
                    return (False, "Can\'t find %s file." % output_file)
                ret.append((input_file, output_file))

        return (True, ret)
