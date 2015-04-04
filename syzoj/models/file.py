from syzoj import oj, db
import zipfile, os
import hashlib
from random import randint
import time


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), unique=True, index=True)
    file = None

    def __init__(self, file):
        self.file = file

        file.seek(0)
        m = hashlib.md5()
        while True:
            data = file.read(8192)
            if not data:
                break
            m.update(data)
        self.filename = m.hexdigest()

    def save(self):
        existed = File.query.filter_by(filename=self.filename).first()
        if existed:
            self = existed
        else:
            self.file.seek(0)
            self.file.save(os.path.join(oj.config['UPLOAD_FOLDER'], self.filename))
            db.session.add(self)
            db.session.commit()

    def parse_as_testdata(self):
        path = os.path.join(oj.config["UPLOAD_FOLDER"], self.filename)
        try:
            zip_file = zipfile.ZipFile(path)
        except:
            return (False, "This file is not zip")

        file_list = zip_file.namelist()

        if "data_rule.txt" not in file_list:
            return (False, "Please include data_rule.txt in testdata pack")
        data_rule = zip_file.read("data_rule.txt")

        lines = data_rule.split('\n')
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace('\r', '').replace('\n', '')

        if len(lines) < 3:
            return (False, "data_rule.txt should include 3 lines")

        data_no = lines[0].split()
        input_name = lines[1]
        output_name = lines[2]

        ret = []

        for i in data_no:
            i = int(i)
            input_file = input_name.replace('#', str(i))
            output_file = output_name.replace('#', str(i))
            if input_file not in file_list:
                return (False, "Do not find %s file" % input_file)
            if output_file not in file_list:
                return (False, "Do not find %s file" % output_file)
            ret.append((input_file, output_file))

        zip_file.close()

        return (True, ret)