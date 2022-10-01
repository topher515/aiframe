from dataclasses import dataclass
import os
import glob
import shutil

import sqlite3

@dataclass
class ImageDataModel:

    img_meta_db = 'img_meta.db'

    def _get_db_cur(self):
        conn = sqlite3.connect(self.img_meta_db)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS img_meta(
                img_path TEXT PRIMARY KEY, 
                rating INT
            );
        """)
        return cur
        
    def get_avail_images(self):
        return glob.glob(os.path.join(os.getcwd(), "imgs", "*"))

    def get_image_rating(self, img_path: str) -> int:
        res = self._get_db_cur().execute("""
            SELECT rating FROM img_meta
            WHERE img_path = ?
        """, [img_path]).fetchone()
        if not res:
            return 0
        rating, = res
        return rating

    def incr_image_rating(self, img_path: str, incr_val: int):
        cur = self._get_db_cur()
        cur.execute("""
            INSERT INTO img_meta(img_path, rating)
            VALUES(?, ?)
            ON CONFLICT(img_path) DO UPDATE SET
                rating = rating + ?
        """, [
            img_path,
            incr_val,
            incr_val
        ])
        cur.connection.commit()
        
    # def get_cur_img_path(self) -> str:
    #     return self.cur_image_path

    # def set_cur_image_path(self, img_path: str):
    #     self.cur_image_path = img_path
        
    def delete_image(self, img_path):
        os.remove(img_path)
    