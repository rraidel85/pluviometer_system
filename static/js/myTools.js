function GetString64FromImageFile(upload_file_component, target_component) {
    var fileReader = new FileReader(),
                files = upload_file_component.files,
                file;
        file = files[0];
        if (!files.length) {
            return;
        }
        if (/^image\/\w+$/.test(file.type)) {
            fileReader.readAsDataURL(file);
            fileReader.onload = function () {
                target_component.src = this.result;
            };
        } else {
            alert("Por favor elija un fichero de imagen.");
        }
}