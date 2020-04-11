#!/usr/bin/python3
import commandify.spotify as sp
import commandify.monitor as monitor
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='control spotify using the\
                                                  commandline')
    parser.add_argument('-i', '--client_id', help='spotify app client_id',
                        required=True)
    parser.add_argument('-s', '--client_secret', help='spotify app client_secret',
                        required=True)
    parser.add_argument('-r', '--redirect_uri', help='redirect uri of the app',
                        required=True)
    parser.add_argument('-l', '--list', metavar='name/link',
                        help='list an album/library/playlist')
    parser.add_argument('-p', '--pause', action='store_true',
                        help='pause the current track')
    parser.add_argument('-u', '--resume', action='store_true',
                        help='resume the current track')
    parser.add_argument('-m', '--monitor', action='store_true',
                        help='start the powerful data collector')
    parser.add_argument('-c', '--current', action='store_true',
                        help='print the current song')
    args = parser.parse_args()

    client_id = args.client_id
    client_secret = args.client_secret
    redirect_uri = args.redirect_uri

    if sp.db_provider.get_access_token() is None:
        print('starting the authentication process...')
        scope = ' '.join(sp.get_scopes())
        auth_code = sp.get_auth_code(client_id, redirect_uri, scope)
        sp.get_refresh_token(client_id, client_secret, auth_code['code'],
                             redirect_uri)
        print('done with authentication')
    access_token = sp.db_provider.get_access_token()
    refresh_token = sp.db_provider.get_refresh_token()
    if sp.access_token_has_expired(access_token):
        print('expired.. requesting new one')
        access_token = sp.get_access_token(client_id, client_secret,
                                           refresh_token['token'])

    if args.pause:
        sp.pause(access_token['token'])
    elif args.resume:
        sp.resume(access_token['token'])
    elif args.monitor:
        monitor.start(client_id, client_secret, refresh_token)
    elif args.current:
        current_track = sp.get_current_track(access_token['token'])
        if current_track is not None:
            print('{} - {}'.format(current_track['item']['name'],
                current_track['item']['artists'][0]['name']))
        else:
            print('no track is playing')
