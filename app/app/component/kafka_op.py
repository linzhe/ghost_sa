# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import sys

from flask import g, current_app

sys.path.append("./")
sys.setrecursionlimit(10000000)
from flask import _app_ctx_stack
from kafka import KafkaProducer, KafkaConsumer
import json
from app.configs import kafka
from app.configs import admin


class CreateKafkaProducer(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def create_producer(self, app):
        app.logger.info('创建kafka producer...')
        return KafkaProducer(bootstrap_servers=app.config['BOOTSTRAP_SERVERS'])

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'kafka_producer'):
            # 超时50s关闭
            ctx.kafka_producer.close(timeout=50)
            current_app.logger.info('正常关闭kafka生产者实例...')

    @property
    def producer(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'kafka_producer'):
                ctx.kafka_producer = self.create_producer()
            return ctx.kafka_producer


def insert_message_to_kafka(key, msg):
    if isinstance(key, str):
        key = key.encode()
    else:
        key = None
    kafka_topic = current_app.config['KAFKA_TOPIC']
    current_app.kafka_producer.send(topic=kafka_topic, key=key, value=json.dumps(msg).encode())


#latest,earliest,none 首次拉取kafka订阅的模式
kafka_offset_reset = 'earliest'


def get_message_from_kafka():
    consumer=KafkaConsumer(kafka.kafka_topic, bootstrap_servers=kafka.bootstrap_servers, group_id=kafka.client_group_id,auto_offset_reset=kafka_offset_reset,client_id='get_message_from_kafka')
    return consumer


def get_message_from_kafka_independent_listener():
    consumer=KafkaConsumer(kafka.kafka_topic, bootstrap_servers=kafka.bootstrap_servers, group_id=admin.independent_listener_kafka_client_group_id,auto_offset_reset=kafka_offset_reset,client_id='get_message_from_kafka_independent_listener')
    return consumer


if __name__ == "__main__":
    insert_message_to_kafka(key='123231231', msg={'msg': 'test'})