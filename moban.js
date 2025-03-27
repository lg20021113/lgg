let nodeData = {}; // 存储 JSON 数据
let nodeKeys = []; // 存储节点的顺序
let currentIndex = 0; // 当前节点索引

// 加载 JSON 数据
async function loadNodeData() {
    try {
        const response = await fetch('node_annotations2.json');
        nodeData = await response.json();
        nodeKeys = Object.keys(nodeData); // 获取节点的顺序
        console.log('节点数据:', nodeData);
        console.log('节点顺序:', nodeKeys);
        updateDisplay(currentIndex); // 初始化显示第一个节点
    } catch (error) {
        console.error('加载节点数据失败:', error);
    }
}

// 更新界面显示
function updateDisplay(index) {
    if (index < 0 || index >= nodeKeys.length) return; // 防止越界

    const nodeId = nodeKeys[index];
    const data = nodeData[nodeId];

    // 更新文本框内容
    const textInput = document.querySelector('.text-box input');
    if (textInput && data.description) {
        textInput.value = data.description;
    }

    // 更新第照片容器内的图片
    const photoContainer = document.querySelector('.photo-container img');
    const photoSection = document.querySelector('.photo-container');
    if (photoContainer && data.photo_paths && data.photo_paths.length > 0) {
        photoContainer.src = `picture/${data.photo_paths[0]}`;
        photoContainer.onload = () => {
            // 确保图片加载完成后调整大小
            const containerWidth = photoSection.clientWidth; // 获取背景容器的宽度
            const containerHeight = photoSection.clientHeight; // 获取背景容器的高度

            photoContainer.style.maxWidth = `${containerWidth}px`;
            photoContainer.style.maxHeight = `${containerHeight}px`;
            photoContainer.style.objectFit = 'contain'; // 保持图片比例
        };
    }

    // 更新相框下方的图片路径名
    const photoSections = document.querySelectorAll('.photo-section');
    photoSections.forEach((section, idx) => {
        const img = section.querySelector('img');
        const label = section.querySelector('.name-label');
        if (img && label) {
            const fileName = img.getAttribute('src').split('/').pop();
            label.textContent = fileName;
        }
    });

    // 更新当前索引
    currentIndex = index;
}

// 更新照片容器的图片
function updatePhoto(newImagePath) {
    const photoContainer = document.querySelector('.photo-container img');
    const photoSection = document.querySelector('.photo-container');
    if (photoContainer) {
        photoContainer.src = newImagePath; // 更新图片路径
        photoContainer.onload = () => {
            // 确保图片加载完成后调整大小
            const containerWidth = photoSection.clientWidth; // 获取容器宽度
            const containerHeight = photoSection.clientHeight; // 获取容器高度
            const imageAspectRatio = photoContainer.naturalWidth / photoContainer.naturalHeight; // 图片宽高比
            const containerAspectRatio = containerWidth / containerHeight; // 容器宽高比

            

            photoContainer.style.objectFit = 'contain'; // 保持图片比例
        };
    }
}

// 跳转到前一个节点
function goToPrevious() {
    if (currentIndex > 0) {
        updateDisplay(currentIndex - 1);
    }
}

// 跳转到后一个节点
function goToNext() {
    if (currentIndex < nodeKeys.length - 1) {
        updateDisplay(currentIndex + 1);
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', async function () {
    await loadNodeData(); // 加载节点数据
});

function goToFirst() {
    alert('1');
}

function goToSecond() {
    alert('2');
}

function goToThird() {
    alert('3');
}

function goToLast() {
    alert('5');
}

// 页面加载时更新图片名称
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有图片和对应的名称标签
    const images = document.querySelectorAll('.photo-container img');
    const labels = document.querySelectorAll('.name-label');
    
    // 更新每个图片下方的名称
    images.forEach((img, index) => {
        // 从图片路径中提取文件名
        const imgPath = img.getAttribute('src');
        const fileName = imgPath.split('/').pop().replace('.png', '');
        // 更新对应的标签文本
        if(labels[index]) {
            labels[index].textContent = fileName;
        }
    });
});

// 用于更新图片和名称的函数
function updateImage(containerIndex, newImagePath) {
    const container = document.querySelectorAll('.photo-section')[containerIndex];
    const img = container.querySelector('img');
    const label = container.querySelector('.name-label');
    
    if(img && label) {
        img.src = newImagePath;
        // 更新名称标签
        const fileName = newImagePath.split('/').pop().replace('.png', '');
        label.textContent = fileName;
    }
};
