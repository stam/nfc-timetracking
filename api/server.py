from flask import Flask, jsonify, request
from settings import SETTINGS
from db import db, Activity, Claim, Tag
from datetime import datetime
from flask.ext.cors import CORS
import json

# basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return 'Hello World!'


@app.route('/activity', methods=['GET'])
def activity_getcollection():
    activities = Activity.get_collection(db.session)
    return jsonify({'data': activities})


@app.route('/tag', methods=['GET'])
def tag_getcollection():
    tags = Tag.get_collection(db.session)
    return jsonify({'data': tags})


@app.route('/claim', methods=['POST'])
def claim_post():
    body = request.json
    # Get tag by tag_code
    tag = db.session.query(Tag).get(body['tag_id'])
    if not tag:
        return "Tag {0} not found".format(body['tag_id'])

    claim = Claim(body['title'], tag)
    db.session.add(claim)

    # If an open activity with that tag exists,
    # link that claim to that activity
    activity = Activity.get_latest_by_tag_id(db.session, tag.id)
    if activity and not activity.ended_at:
        activity.claim = claim

    db.session.commit()
    return json.dumps(Claim.transform(claim))


@app.route('/activity/in', methods=['POST'])
def activity_checkin():
    body = request.json
    # Get tag by tag_code
    tag = db.session.query(Tag).filter(Tag.code == body['tag_code']).first()
    if not tag:
        tag = Tag(body['tag_code'])
        db.session.add(tag)

    activity = Activity.get_latest_by_tag_id(db.session, tag.id)

    # If an activity for that tag still is open, error
    if activity and not activity.ended_at:
        return "Activity {0} still open for this tag".format(activity.id)

    # If a claim for tag exists, set that claim
    claim = Claim.get_latest_by_tag_id(db.session, tag.id)

    activity = Activity(tag, claim)
    db.session.commit()
    return json.dumps(Activity.transform(activity))


@app.route('/activity/out', methods=['POST'])
def activity_checkout():
    body = request.json
    tag = db.session.query(Tag).filter(Tag.code == body['tag_code']).first()
    if not tag:
        return 'Tag {0} not found!'.format(body['tag_code'])

    activity = Activity.get_latest_by_tag_id(db.session, tag.id)

    if activity.ended_at:
        return 'Activity {0} already checked out'.format(activity.id)

    activity.ended_at = datetime.utcnow()
    db.session.commit()
    return json.dumps(Activity.transform(activity))

if __name__ == '__main__':
    app.run(debug=SETTINGS['DEBUG'])
