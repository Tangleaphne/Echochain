/*****************************************
         * 1) Define multiple providers in web3Modal
         *****************************************/
const providerOptions = {
    // 1) Injected (MetaMask, Brave, Opera, etc.)
    injected: {
        display: {
        name: 'MetaMask'
        },
        package: null
    },
    // 2) WalletConnect
    walletconnect: {
        package: window.WalletConnectProvider.default,
        options: {
        infuraId: 'f37c8f03e94d4418805156e20d7fe1ab'
        }
    },
    // 3) Fortmatic
    fortmatic: {
        package: window.Fortmatic,
        options: {
        key: 'pk_live_A64FBB4A383441A7'
        }
    },
    // 4) Torus
    torus: {
        package: window.Torus,
        options: {}
    }
    };

    // Create web3Modal
    const web3Modal = new window.Web3Modal.default({
        cacheProvider: true,
        providerOptions
    });

    let ethersProvider, signer;
    let currentAddress = ''; // track address

    /*******************************
     * 2) open/close popups
     *******************************/
    function openPopup(id) {
        document.querySelectorAll('.wallet-popup').forEach(p => p.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }
    function closePopup(id) {
        document.getElementById(id).classList.remove('active');
    }
    function goBack(prevId) {
        const currentId = event.target.closest('.wallet-popup').id;
        closePopup(currentId);
        openPopup(prevId);
    }

    /*******************************
     * 3) Main button logic
     *******************************/
    const mainBtn = document.getElementById('wallet-main-btn');
    const mainText = document.getElementById('wallet-main-text');

    // If not connected => open custom-popup
    // If connected => open user-info-popup
    mainBtn.addEventListener('click', () => {
        if (!currentAddress) {
            // show custom connect
            openPopup('custom-popup');
        } else {
            // show user info
            showUserInfoPopup();
        }
    });

    // \"Get Started\" => link to wc wallet guide
    document.getElementById('get-started-btn').addEventListener('click', function(){
    window.open('https://walletguide.walletconnect.network/?type=wallet', '_blank');
    });

    // Hide custom popup on 'all wallets', then show #wallet-list
    document.getElementById('all-wallets-btn').addEventListener('click', () => {
    closePopup('custom-popup');
    openPopup('wallet-list');
    });

    /********************************************
     * 4) All wallets with providerId
     ********************************************/
    const allWallets = [
    { name: 'MetaMask',      providerId: 'injected'      },
    { name: 'WalletConnect', providerId: 'walletconnect' },
    { name: 'Fortmatic',     providerId: 'fortmatic'     },
    { name: 'Torus',         providerId: 'torus'         },
    { name: 'Trust Wallet',  providerId: 'walletconnect' },
    { name: 'OKX Wallet',    providerId: 'walletconnect' }
    ];

    const walletContainer = document.getElementById('wallet-container');

    // card layout
    function renderWallets(list) {
    walletContainer.innerHTML = '';
    list.forEach(item => {
        const card = document.createElement('div');
        card.className = 'wallet-card';
        card.onclick = () => connectWallet(item.providerId);

        card.textContent = item.name;
        walletContainer.appendChild(card);
    });
    }
    renderWallets(allWallets);

    function filterWallets() {
    const input = document.getElementById('wallet-search').value.toLowerCase();
    const filtered = allWallets.filter(w => w.name.toLowerCase().includes(input));
    renderWallets(filtered);
    }

    /**********************************************
     * 5) connectWallet(providerId) => web3Modal.connectTo
     **********************************************/
    async function connectWallet(providerId) {
    let address = '';
    try {
        const instance = await web3Modal.connectTo(providerId);
        ethersProvider = new ethers.providers.Web3Provider(instance);
        signer = ethersProvider.getSigner();
        address = await signer.getAddress();
        currentAddress = address; // store globally
        await updateMainButton(address);

    } catch (err) {
        console.error('connectWallet error', err);
    } finally {
        if(!currentAddress) {
        // no address => re-show #wallet-list
        openPopup('wallet-list');
        } else {
        // success => close #wallet-list
        closePopup('wallet-list');
        }
    }
    }

    async function updateMainButton(address) {
    // e.g. 0x1234...abcd
    const shortened = address.slice(0, 6) + '...' + address.slice(-4);
    mainText.textContent = shortened;
    }

    /**********************************************
     * 6) showUserInfoPopup => fetch balance, show address, etc.
     **********************************************/
    async function showUserInfoPopup() {
    try {
        // get address from global
        const address = currentAddress;
        const userAddressEl = document.getElementById('user-address');
        const userBalanceEl = document.getElementById('user-balance');

        userAddressEl.textContent = `Address: ${address}`;

        // fetch balance
        const balance = await ethersProvider.getBalance(address);
        const ethBalance = ethers.utils.formatEther(balance);
        userBalanceEl.textContent = `Balance: ${Number(ethBalance).toFixed(4)} ETH`;

        openPopup('user-info-popup');
    } catch (err) {
        console.error('showUserInfoPopup error', err);
    }
    }

    // handle disconnect
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', async () => {
        try {
            // clear local state
            currentAddress = '';
            mainText.textContent = 'Wallet Connect';
            closePopup('user-info-popup');

            // Clear web3Modal's cached provider
            web3Modal.clearCachedProvider();
            if(ethersProvider && ethersProvider.provider && ethersProvider.provider.disconnect) {
                await ethersProvider.provider.disconnect();
            }
            ethersProvider = null;
            signer = null;
        } catch(err) {
            console.error('logout error', err);
        }
    });

    // 页面加载后，可执行如下检查，若有cachedProvider说明上一次连接过
    window.onload = async () => {
        if (web3Modal.cachedProvider) {
            try {
                const instance = await web3Modal.connect(); 
                ethersProvider = new ethers.providers.Web3Provider(instance);
                signer = ethersProvider.getSigner();
                currentAddress = await signer.getAddress();
                updateMainButton(currentAddress); 
                // 让你的按钮或UI显示短地址
            } catch (err) {
                console.error('自动重连失败', err);
            }
        }
    };