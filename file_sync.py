import datetime
import os
import paramiko
from stat import S_ISDIR


def main():
    # get a list of local files to sync
    local_files, local_folders = get_local_files()
    # # compare with last run list to see if anything changed.
    local_local_same, new_files = compare_files(local_files, last_run)
    print local_local_same, new_files
    # get a list of servers to check
    servers = get_servers()

    for server in servers:
        # Connect to remote server
        sftp = connect_to_server(server)

        # remote to server and get a list file files on it and a sorted list of folders.
        remote_files, remote_folders = get_remote_files(sftp)

        # compare local to remote list to determine what will be copied over
        local_remote_same, needs_copied = compare_files(local_files, remote_files)
        print(local_remote_same, needs_copied)

        # compare remote to local to determine what will be deleted
        remote_local_same, needs_deleted = compare_files(remote_files, local_files)
        print(remote_local_same, needs_deleted)

        # do the actual copy
        #copy_files(needs_copied, sftp)
        # do the actual delete
        #delete_files(needs_deleted, sftp)

        # Clean up Empty folders
        find_all_folders(octoprint_path, sftp)
        #remote_local_folders_same, delete_folders = compare_folders2(remote_folders, local_folders)
        #delete_empty_folders(delete_folders)

        # Close server connection
        sftp.close()


def get_local_files():
    # get a list of local files to sync
    local_files = []
    local_folders = []
    for root, subFolders, files in os.walk(local_path):
        for file in files:
            if 'metadata.json' not in file:
                print("{}/{}".format(root[7:], file))
                local_files.append("{}/{}".format(root[7:], file))
        if root not in local_folders:
            if root != local_path:
                local_folders.append(root[7:])
    print local_files
    print local_folders
    return local_files, local_folders


def compare_files(set1, set2):
    # compare with last run list to see if anything changed.
    # compare local to remote list to determine what will be copied over
    # compare remote to local to determine what will be deleted
    there = []
    not_there = []
    for item in set1:
        if item not in set2:
            not_there.append(item)
        elif item in set2:
            there.append(item)
    if len(not_there) == 0:
        # all files are the same
        return 0, not_there
    else:
        return 1, not_there


def compare_folders(set1, set2):
    # compare with last run list to see if anything changed.
    # compare local to remote list to determine what will be copied over
    # compare remote to local to determine what will be deleted
    there = []
    not_there = []
    for item in set1:
        print item[34:]
        if item[34:] not in set2:
            not_there.append(item)
        elif item[34:] in set2:
            there.append(item)
    if len(not_there) == 0:
        # all folders are the same
        return 0, not_there
    else:
        return 1, not_there


def compare_folders2(set1, set2):
    # compare with last run list to see if anything changed.
    # compare local to remote list to determine what will be copied over
    # compare remote to local to determine what will be deleted
    there = []
    not_there = []
    for item in set1:
        print item
        if item not in set2:
            not_there.append(item)
        elif item in set2:
            there.append(item)
    if len(not_there) == 0:
        # all folders are the same
        return 0, not_there
    else:
        return 1, not_there


def compare_folders_create(set1, set2):
    # compare with last run list to see if anything changed.
    # compare local to remote list to determine what will be copied over
    # compare remote to local to determine what will be deleted
    there = []
    not_there = []
    for item in set1:
        print item
        if item not in set2:
            not_there.append(item)
        elif item in set2:
            there.append(item)
    if len(not_there) == 0:
        # all folders are the same
        return 0, not_there
    else:
        return 1, not_there


def get_servers():
    # get a list of servers to check
    servers = ['unraid.barragree.net']
    return servers


def connect_to_server(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connectiong to: {}")
    ssh.connect(hostname=server, username="abarragree", key_filename='/Users/abarragree/.ssh/id_rsa')
    print("Connected to: {}")
    sftp = ssh.open_sftp()
    return sftp


def get_remote_files(sftp):
    # remote to server and get a list file files on it.
    remote_files = []
    remote_folders = []
    for path, files in sftp_walk(octoprint_path, sftp):
        for file in files:
            if 'metadata.json' not in file:
                print("{}/{}".format(path[34:], file))
                remote_files.append("{}/{}".format(path[34:], file))
                if path[34:] not in remote_folders:
                    remote_folders.append(path[34:])
    print remote_files
    sorted_remote_folders = sort_folders_decending(remote_folders)
    print("Folders: {}".format(sorted_remote_folders))

    return remote_files, sorted_remote_folders


def sftp_walk(remotepath, sftp):
    # Walks a remote servers path provided
    path = remotepath
    files = []
    folders = []
    for f in sftp.listdir_attr(remotepath):
        if S_ISDIR(f.st_mode):
            folders.append(f.filename)
        else:
            files.append(f.filename)
    if files:
        yield path, files
    for folder in folders:
        new_path = os.path.join(remotepath, folder)
        for x in sftp_walk(new_path, sftp):
            yield x


def find_all_folders(remotepath, sftp):
    path = remotepath
    folders = []
    for f in sftp.listdir_attr(remotepath):
        if S_ISDIR(f.st_mode):
            folders.append(f.filename)
    for folder in folders:
        new_remotepath = "{}/{}".format(remotepath, folder)
        more_folders = find_all_folders(new_remotepath, sftp)
        for folder in more_folders:
            folders.append(folder)
    return folders


def copy_files(files, sftp):
    # do the actual copy
    for file in files:
        print("copy: {}{} to {}{}".format(local_path, file, octoprint_path, file))
        try:
            sftp.put("{}{}".format(local_path, file), "{}{}".format(octoprint_path, file))
        except IOError:
            test = file.split("/")
            current_folder = ''
            for folder in test[1:-1]:
                current_folder = "{}/{}".format(current_folder, folder)
                try:
                    sftp.mkdir("{}{}".format(octoprint_path, current_folder))
                except IOError:
                    pass
            sftp.put("{}{}".format(local_path, file), "{}{}".format(octoprint_path, file))


def delete_files(files, sftp):
    for file in files:
        print("Delete: {}{}".format(octoprint_path, file))
        sftp.remove("{}{}".format(octoprint_path, file))

    pass


def sort_folders_decending(folders):
    split_folders = []
    for folder in folders:
        split_folder = folder.split("/")
        print(split_folder)
        split_folders.append(split_folder)
    print split_folders
    split_folders.sort(key=len, reverse=True)

    nicely_sorted_folder_list = []
    for folder in split_folders:
        string_folder = "/".join(str(e) for e in folder)
        print string_folder
        nicely_sorted_folder_list.append(string_folder)
    print("Sorted: {}".format(nicely_sorted_folder_list))
    return nicely_sorted_folder_list


def sort_folders_acending(folders):
    split_folders = []
    for folder in folders:
        split_folder = folder.split("/")
        print(split_folder)
        split_folders.append(split_folder)
    print split_folders
    split_folders.sort(key=len)

    nicely_sorted_folder_list = []
    for folder in split_folders:
        string_folder = "/".join(str(e) for e in folder)
        print string_folder
        nicely_sorted_folder_list.append(string_folder)
    print("Sorted: {}".format(nicely_sorted_folder_list))
    return nicely_sorted_folder_list


def delete_empty_folders(folders):
    pass



if __name__ == '__main__':
    octoprint_path = '/home/abarragree/3dprinter/uploads'
    local_path = './files'
    last_run = []
    main()
